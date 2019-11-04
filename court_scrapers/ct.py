import datetime
import time
import random
from bs4 import BeautifulSoup
from court_scrapers.core import CaseInfo, SeleniumBase
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
        self._clear_date_form() # just to ensure this is blank before starting
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

    def _get_case_table(self):
        return self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_gvCourtEventsResults")

    def _get_pagination(self):
        table = self._get_case_table()
        # TODO: Handle single page (pagination doesn't exist there)
        # Something as simple as 
        # elem = table.find_element_by_css_selector("tr.grdBorder")
        # return [None] if elem is None else elem.find_element_by_tag_name("table").find_elements_by_tag_name("td")
        return table.find_element_by_css_selector(
            "tr.grdBorder"
            ).find_element_by_tag_name(
                "table"
            ).find_elements_by_tag_name("td")

    def _get_docket_numbers(self):
        docket_nums = set()
        num_pages = len(self._get_pagination())
        for i in range(num_pages):
            table = self._get_case_table().find_element_by_tag_name("tbody")
            docket_nums |= set(
                (elem.find_element_by_tag_name("a").text 
                for elem in table.find_elements_by_css_selector("tr.grdRow"))
                )
            docket_nums |= set(
                (elem.find_element_by_tag_name("a").text 
                for elem in table.find_elements_by_css_selector("tr.grdRowAlt"))
                )
            pagination = self._get_pagination()
            # TODO: Handle/check for empty case list
            if len(pagination) == i + 1:
                break
            pagination[i + 1].click()
        return docket_nums

    def _get_case_detail(self, case):
        case_url = "http://civilinquiry.jud.ct.gov/LoadDocket.aspx?DocketNo={}".format(case)
        self.driver.get(case_url)
        case_type = self.driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_CaseDetailBasicInfo1_lblBasicCaseType"
            ).text.strip()
        # TODO: Parties
        date_file_html = self.driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_CaseDetailHeader1_lblFileDate"
        ).get_attribute("outerHTML")
        date_filed = BeautifulSoup(
            date_file_html, "html.parser"
        ).span.find(text=True, recursive=False).strip()
        court_location = self.driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_CaseDetailBasicInfo1_lblBasicLocation"
        ).text.strip()
        return CaseInfo(
            case_num=case, 
            case_type=case_type,
            date_filed=datetime.datetime.strptime(date_filed, "%m/%d/%Y").date(), 
            plaintiff_parties=[],
            plaintiff_attnys=[],
            def_parties=[],
            def_attnys=[],
            court_location=court_location
            )

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
        cases = []
        self._submit_date_query(case_date, case_category)
        try:
            docket_nums = self._get_docket_numbers()
        except Exception as e:
            print(e)
            breakpoint()
        for case in docket_nums:
            cases.append(self._get_case_detail(case))
            time.sleep(random.random() * 2) # be a *little* bit nice on their servers
        return cases
        
                

