import re
import logging
import datetime
import time
import random
from bs4 import BeautifulSoup
from court_scrapers.core import CASE_FIELDS, CaseInfo, SeleniumBase
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
        pagination_items = []
        table = self._get_case_table()
        page_element = table.find_elements_by_css_selector("tr.grdBorder")
        if page_element == []:
            return [None]
        page_list = table.find_element_by_css_selector(
            "tr.grdBorder"
            ).find_element_by_tag_name(
                "table"
            ).find_elements_by_tag_name("td")
        for item in page_list:
            links = item.find_elements_by_tag_name("a")
            if links == []:
                pagination_items.append(None)
            else:
                pagination_items.append(links[0])
        return pagination_items

    def _get_next_page(self, pagination, current_page=1):
        link_pages = [
            link.get_attribute("href").replace(
                "javascript:__doPostBack('ctl00$ContentPlaceHolder1$gvCourtEventsResults','Page$", ""
                ).replace("')", "")
            if link is not None
            else None
            for link in pagination
            ]
        if str(current_page + 1)  in link_pages:
            return link_pages.index(str(current_page + 1))
        return None

    def _get_docket_numbers(self, current_docket_nums=set(), current_page=1):
        table = self._get_case_table().find_element_by_tag_name("tbody")
        current_docket_nums |= set(
            (elem.find_element_by_tag_name("a").text
            for elem in table.find_elements_by_css_selector("tr.grdRow"))
        )
        current_docket_nums |= set(
            (elem.find_element_by_tag_name("a").text
            for elem in table.find_elements_by_css_selector("tr.grdRowAlt"))
        )
        pagination = self._get_pagination()
        next_page = self._get_next_page(pagination, current_page)
        if next_page is not None:
            pagination[next_page].click()
            self._get_docket_numbers(current_docket_nums, current_page=current_page+1)
            pagination = self._get_pagination()
        return current_docket_nums

    def _get_parties(self):
        all_parties = []
        party_div = self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_CaseDetailParties1_gvParties")
        # just get immediate children tr
        parties = party_div.find_element_by_tag_name("tbody").find_elements_by_xpath("./tr")
        for party in parties[1:]:
            # I think this gets all id elements 1 node deep into path but not sure
            party_info = {
                "party_type": None,
                "name": None,
                "attorney": None
            }
            for party_detail in party.find_elements_by_xpath(".//*[@id]"):
                # need this approach because rows have automatically generated ids
                if party_detail.get_attribute("id").endswith("PlaintDefPartyNo"):
                    party_type = re.search(r"([A-Z])\-\d{2}", party_detail.text).group(1)
                    if party_type == "P":
                        party_info["party_type"] = "plaintiff"
                    elif party_type == "D":
                        party_info["party_type"] = "defendant"
                    else:
                        party_info["party_type"] = "other"
                if party_detail.get_attribute("id").endswith("AttyInfo"):
                    party_info["attorney"] = party_detail.text.replace("Attorney:","").strip().split("\n")[0]
                if party_detail.get_attribute("id").endswith("PartyName"):
                    party_info["name"] = party_detail.text.strip()
            all_parties.append(party_info)
        return all_parties


    def _get_case_detail(self, case):
        case_url = "http://civilinquiry.jud.ct.gov/LoadDocket.aspx?DocketNo={}".format(case)
        self.driver.get(case_url)
        case_type = self.driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_CaseDetailBasicInfo1_lblBasicCaseType"
            ).text.strip()
        date_file_html = self.driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_CaseDetailHeader1_lblFileDate"
        ).get_attribute("outerHTML")
        # https://stackoverflow.com/questions/27195569/how-to-get-text-from-within-a-tag-but-ignore-other-child-tags?noredirect=1&lq=1
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
            parties=self._get_parties(),
            court_location=court_location
            )

    def _query_has_no_events(self):
        lbl_error = self.driver.find_elements_by_id("ctl00_ContentPlaceHolder1_lblError")
        return len(lbl_error) > 0 and lbl_error[0].text != ""

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
        if self._query_has_no_events():
            # return empty list if there are no resulting events
            return cases
        docket_nums = self._get_docket_numbers()
        for case in docket_nums:
            try:
                case_detail = self._get_case_detail(case)
                cases.append(case_detail)
            except Exception as e:
                case_info = CaseInfo(
                    case_num=case,
                    **dict({field:None for field in CASE_FIELDS if field != "case_info"})
                    )
                cases.append(case_info)
                logging.error(e)
            time.sleep(random.random() * 2) # be nice to their servers
        return cases
        
                

