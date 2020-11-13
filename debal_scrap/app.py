import pandas as pd

from debal_scrap.models import Debal


def app():
    debal = Debal()
    group = debal.select_group()

    data = list(group.expenses())
    df = pd.DataFrame(data)
    df.to_csv(input("save as <filename.csv>: "))
