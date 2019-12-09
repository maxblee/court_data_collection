import contextlib
import datetime
import collections
from court_scrapers.errors import InvalidQueryError
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

CASE_FIELDS = [
    "case_num", "case_type", "date_filed", "parties", "court_location"
]

CaseInfo = collections.namedtuple("CaseInfo", CASE_FIELDS)

class SeleniumBase(object):

    BASE_URL = None

    def __init__(self, start_url=None, headless=True, exec_path=None):
        self.BASE_URL = start_url if start_url is not None else self.BASE_URL
        if self.BASE_URL is None:
            raise ValueError("You must have a starting URL with the attribute BASE_URL")
        opts = Options()
        opts.headless = headless
        if exec_path is not None:
            self.driver = webdriver.Firefox(options=opts, executable_path=exec_path)
        else:
            self.driver = webdriver.Firefox(options=opts)
        self.driver.get(self.BASE_URL)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.quit()

    def _validate_date(self, date_type):
        """Determines whether a given date is valid. Raises an error if not"""
        if not isinstance(date_type, datetime.date):
            raise TypeError("You must enter a `datetime.date` type")

    def _validate_date_range(self, start_date, end_date):
        """Determines whether a date range is valid (i.e. if the start_date is before the end_date and both are dates)"""
        self._validate_date(start_date)
        self._validate_date(end_date)
        if not start_date <= end_date:
            raise InvalidQueryError("The start date must come before the end date. {} comes after {}".format(start_date, end_date))

    def __get_date_range(self, start_date, end_date):
        while start_date <= end_date:
            start_date += datetime.timedelta(days=1)
            yield start_date

    def get_court_cases(self, date_type):
        """Returns all of the court cases that had hearings on a given day."""
        raise NotImplementedError

    def collect_cases(self, start_date, end_date):
        """Collects every court case occuring within a given date range."""
        self._validate_date_range(start_date, end_date)
        cases = set()
        for weekday in self.__get_date_range(start_date, end_date):
            cases |= self.get_court_cases(weekday)
        return cases