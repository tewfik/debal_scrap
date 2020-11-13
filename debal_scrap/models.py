from __future__ import annotations

import datetime
from urllib.parse import urljoin
from typing import Dict, List

from bs4 import BeautifulSoup
from iterfzf import iterfzf

from debal_scrap.utils import flatten
from debal_scrap.http import ThrottledSessionFactory, SessionFactoryMixin


BASE_URL = "https://www.debal.fr"


class Debal(SessionFactoryMixin):
    """Documentation for Debal"""

    def __init__(self):
        self.session_factory = ThrottledSessionFactory()
        self.groups = self._login()

    def _login(self) -> Dict[str, str]:
        body = {
        }

        resp = self.session.post(f"{BASE_URL}/users/login", data=body)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        groups = {
            group.p.text: group.attrs["href"]
            for group in soup.find_all(class_="group-list")
        }

        return groups

    def select_group(self) -> Group:
        group_name = iterfzf(self.groups)
        group_href = self.groups[group_name]

        return Group(self.session_factory, group_href)


class Group(SessionFactoryMixin):
    def __init__(self, session_factory: ThrottledSessionFactory, group_href: str):
        self.session_factory = session_factory
        self.group_href = group_href

    def expenses(self):
        return flatten([page.expenses() for page in self.iter_pages()])

    def iter_pages(self):
        page = Page(
            self.session_factory,
            urljoin(BASE_URL, f"{self.group_href}/listing"),
        )
        yield page

        while (page := page.next_page()):
            print(".", end="", flush=True)
            yield page

        print()


class Page(SessionFactoryMixin):
    def __init__(self, session_factory: ThrottledSessionFactory, url: str):
        self.session_factory = session_factory

        resp = self.session.get(url)
        resp.raise_for_status()

        self.soup = BeautifulSoup(resp.text, "html.parser")

    def next_page(self):
        """Return the next page or None"""
        try:
            next_url = urljoin(
                BASE_URL,
                self.soup.find_all(class_="next")[0].a.attrs["href"],
            )
        except IndexError:
            return None

        return Page(self.session_factory, next_url)

    def expenses(self):
        for month in self.find_months():
            year = self.month_details(month)
            for expense in self.find_expenses(month):
                yield self.expense_details(expense, year)

    def find_months(self):
        return self.soup.find(class_="list").find_all("ul")

    def month_details(self, month) -> int:
        """Return the year"""
        return int(
            month.find(class_="listing-header").span.text.strip().split()[-1]
        )

    def find_expenses(self, month):
        return month.find_all(class_="listing-entry")

    def expense_details(self, expense, year):
        day, month, category = expense.find_all("p")
        day = int(day.text)
        month = int(month.text.split()[-1])
        category = category.attrs["class"][-1]

        return {
            "created_at": datetime.date(year, month, day),
            "category": category,
            "title": expense.find(class_="entry-link").text,
            "paid_by": expense.find(class_="text-info").text,
            "paid_for": self.find_beneficiaries(expense),
            "amount": float(expense.find(class_="listing-entry-amount").text.split()[0]),
        }

    def find_beneficiaries(self, expense) -> List[str]:
        try:
            # multiple beneficiaries
            beneficiaries = [beneficiary.text.strip() for beneficiary in expense.find(class_="beneficiary-list").find_all("span")]
        except AttributeError:
            # single beneficiary => no element with class=""beneficiary-list""
            beneficiaries = [expense.find(class_="beneficiary-list-link").text.strip()]

        return beneficiaries
