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

### API

All of these scrapers are designed to be fairly easy to use from the perspective of an end-user. All of the scrapers support the same basic
syntax using Python's `with` syntax.

In order to get all cases occurring on a single date, simply type:

```python
from datetime import date
from court_scrapers.<2-digit state abbreviation> import <Scraper Name>

date_query = date(year, month, day)

with <Scraper Name> as court_cases:
    query_results = court_cases.get_court_cases(date_query)
```

Getting all cases in a date range is similarly easy:

```python
with <Scraper Name> as court_cases:
    query_results = court_cases.collect_cases(start_date, end_date)
```

### Developer Guide

From the perspective of a developer, it's a little bit more complicated, but not too much. The scrapers generally interact with an abstract base class, `SeleniumBase`. That base class has a number of convenience methods, like simple date validation, designed to reduce the amount of code developers writing future scrapers will need to write. 

However, in some cases, you might need to override those methods. So keep in mind that the base class does default to validating date queries and to compiling cases using `collect_cases` by iterating over `get_court_cases`.

Additionally, cases should generally contain the followinng fields:

```python
CASE_FIELDS = [
    "case_num", "case_type", "date_filed", "parties", "court_location"
]
```

## States

### Connecticut

`ConnecticutCivil`

- Courts supported: Civil court
- Date queries only work on dates occurring on a given date or in the future. The Connecticut court search system for civil court does not allow you to query dates occurring in the past. For this reason, people considering using this tool should likely consider running only `get_court_cases` and using a scheduler (like a cron job on an EC2 instance) to update the cases.

## Steps Forward

From here, there are a few places where I really need to improve the script. 

1. First of all, the error handling on this should be improved, particularly in how it handles duplicate cases. Right now, I'm using sets to reduce the number of duplicate rows, but without even handling whitespace trimming, the accury of these deduplication efforts is pretty limited.
2. This tool should ideally enable people to update based on a running database of collected court cases (especially since Conntecticut does not allow you to query historic civil cases). 
3. Finally, we need to add more states into this database. I know for a fact that Virginia has a) a unified court system and b) a court system with date fields that would allow you to write similar scrapers. I imagine other states do as well.

