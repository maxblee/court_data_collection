import datetime
import collections
from court_scrapers.errors import InvalidQueryError
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

CaseInfo = collections.namedtuple("CaseInfo", [
    "case_num", "case_type", "date_filed", "plaintiff_parties", "plaintiff_attnys",
    "def_parties", "def_attnys", "court_location"
])

class SeleniumBase:

    BASE_URL = None

    def __init__(self, processed_cases=[], start_url=None, headless=True, exec_path=None):
        # TODO: Make this more robust, so it supports case loads > RAM
        # (probably by using SQL)
        self.cases = processed_cases
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
