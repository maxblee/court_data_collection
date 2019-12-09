import pytest
import datetime
import re
import math
from court_scrapers.ct import ConnecticutCivil

def get_nearest_weekend():
    today = datetime.date.today()
    # 13 so we're always looking ahead (not on today)
    # this is necessary because datetime.today() will currently break
    # because I don't understand the logic behind connecticut's date parsing
    return today + (datetime.timedelta(days=13 - today.weekday()))

def test_empty_cases_returns_empty_list():
    with ConnecticutCivil() as ct:
        cases = ct.get_court_cases(get_nearest_weekend())
    assert len(cases) == 0
    assert cases == []

def test_goes_to_all_pages():
    # Makes sure the number of cases on entry page == number of total cases
    today = datetime.date.today()
    day_to_scrape = today if today.weekday() < 5 else today + datetime.timedelta(days=2)
    with ConnecticutCivil(headless=False) as ct_scraper:
        ct_scraper._submit_date_query(day_to_scrape)
        current_page = 1
        num_records_text = ct_scraper.driver.find_element_by_id("ctl00_ContentPlaceHolder1_lblRecords").text
        num_expected = int(re.findall(r"[0-9]{4}$", num_records_text.strip())[0])
        while True:
            pagination = ct_scraper._get_pagination()
            next_idx = ct_scraper._get_next_page(pagination, current_page)
            if next_idx is not None:
                pagination[next_idx].click()
                current_page += 1
            else:
                break
    assert math.ceil(num_expected / 200) == current_page

# TODO: handle single-page pagination on docket collection
# (The problem with this is the constraints of ct make it hard to do reliably)

