# Court Data Collection Project

This is a project designed to collect court-specific information for a set
of cases that have unified court systems (i.e. where there is a single court
database system for the entire state or for large portions of the state).

Throughout this README, you'll see information about which court cases we've collected data from
and what information we're collecting using individual scrapers.

## Table of Contents

- **[Structure](#structure)**
- **[States](#states)**
    - **[Connecticut](#connecticut)**

## Structure

All of these scrapers are designed to be fairly easy to use from the perspective of an end-user.

All of the scrapers support context managers, in order to close Selenium's webdriver at the end
of a successful or failing run (without having to deal with `try/except/finally` logic). And the general
syntax for all of the requests should be the same:

```python
from datetime import date
from court_scrapers.<2-digit state abbreviation> import <Scraper Name>

start_date = date(Integer Year, Integer Month, Integer Day)
end_date = date(Integer Year, Integer Month, Integer Day)

with <Scraper Name> as court_cases:
    date_query_results = court_cases.get_cases(start_date, end_date)
```

## States

### Connecticut

#### Courts Supported
Connecticut currently only has support in its scrapers for Civil and Family courts.

In order to query Connecticut's Civil cases, type:

```python
from court_scrapers.ct import ConnecticutCivil
import datetime

with ConnecticutCivil() as ct_cases:
    ct_results = ct_cases.get_court_cases(datetime.date.today())
```

For the family courts, you only have to make a minor change:
```python
...
with ConnecticutCivil() as ct_cases:
    ct_results = ct_cases.get_court_cases(datetime.date.today(), case_category="family")
```

#### Limitations
The date querying support for Connecticut's Civil and Family courts is limited exclusively
to court cases on a given date or in the future. Because of that, you cannot use this tool to query
dates that have previously occurred. For practical purposes, this means that you'll probably want to
run this query using cron in a cloud-based computing platform (like an EC2 instance).

The other option for collecting data requires making a request directly to the court, though, so this
at least provides a decent mechanism for keeping an updated log of court cases in the state.

