import requests
import time


ANTI_FLOOD_LIMIT = 3


class ThrottledSessionFactory:
    """Documentation for HttpSession

    """
    def __init__(self):
        self.last_call_time = None
        self._session = requests.Session()

    def get_session(self):
        self.wait_flood_guard()
        return self._session

    def wait_flood_guard(self):
        if self.last_call_time is not None:
            now = time.perf_counter()
            elapsed = now - self.last_call_time
            time.sleep(
                max(0, ANTI_FLOOD_LIMIT - elapsed)
            )

        self.last_call_time = time.perf_counter()


class SessionFactoryMixin:
    def __init__(self, *args, **kwargs):
        "docstring"
        super().__init__(*args, **kwargs)

    @property
    def session(self):
        return self.session_factory.get_session()
