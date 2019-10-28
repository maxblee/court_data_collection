import datetime
from court_scrapers.core import SeleniumBase
from court_scrapers.errors import InvalidQueryError

class ConnecticutCivil(SeleniumBase):

    BASE_URL = "http://civilinquiry.jud.ct.gov/CourtEventsSearchByDate.aspx"

    def _validate_date(self, case_date):
        # This makes sure we're dealing with a datetime.date format
        super()._validate_date(case_date)
        if case_date < datetime.date.today():
            raise InvalidQueryError("The date you enter must occur today or in the future")

    def _clear_date_form(self):
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtDate").clear()

    def _submit_date_query(self, case_date, case_category="civil"):
        self._validate_date(case_date)
        str_date = case_date.strftime("%m/%d/%Y")
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtDate").send_keys(str_date)
        if case_category.lower().strip() != "civil":
            if case_category.lower().strip() == "family":
                self.driver.find_element_by_xpath(
                    "//select[@id='ctl00_ContentPlaceHolder1_ddlCaseCategory']/option[@value='FA']"
                    ).click()
            else:
                raise InvalidQueryError("The only valid case categories are 'civil' and 'family'")
        # TODO: Add support for specifying single location 
        # (This winds up being somewhat tricky bc lots of locations)
        # (and need something robust but still user-friendly)
        self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSubmit").click()


    def get_court_cases(self, case_date, case_category="civil"):
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
        self._submit_date_query(case_date, case_category)
        return self._get_case_data()

    def _get_case_data(self):
        case_data = []
        current_page = 1
        has_next_page = True
        while has_next_page:
            # TODO: Get data
            next_page = self._get_next_page(current_page)
            current_page+=1
            if next_page is None:
                has_next_page = False
            else:
                next_page.click()
        return case_data


    def _get_next_page(self, current_page=1):   # current_page is 1-indexed
        table = self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_gvCourtEventsResults")
        pages = table.find_element_by_css_selector(
            "tr.grdBorder"
            ).find_element_by_tag_name(
                "table"
            ).find_elements_by_tag_name("td")
        if current_page == len(pages):  # if you're on the last page
            return None
        return pages[current_page]
        
                

