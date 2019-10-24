import datetime
from scrapers.base_scrapers import SeleniumBase
from scrapers.errors import InvalidQueryError

class ConnecticutCivil(SeleniumBase):

    BASE_URL = "http://civilinquiry.jud.ct.gov/CourtEventsSearchByDate.aspx"

    def _validate_date(self, date_type):
        super()._validate_date(date_type)
        if date_type < datetime.date.today():
            raise InvalidQueryError("The date you enter must occur today or in the future")

    def _clear_date_form(self):
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtDate").clear()

    def get_court_cases(self, case_date):
        """Returns a list of dictionaries of all of the court cases occuring on a given day

        Parameters
        ----------
        case_date: datetime.date
            The date when a case is occuring. Must be *in the future, or today* because of website constraints
        
        Raises
        ------
        InvalidQueryError
            If the date you present is in the past (or isn't a datetime)
        """
        str_date = case_date.strftime("%m/%d/%Y")
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtDate").send_keys(str_date)
        # TODO: Handle other filtering
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSubmit").click()
        # TODO: Handle switching to other court cases, handling pagination
        self._handle_case_pages()

    def _handle_case_pages(self):
        pass