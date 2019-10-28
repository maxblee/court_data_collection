import datetime
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

def test_single_page_case():
    pass


