import datetime
from scrapers.base_scrapers import SeleniumBase
from scrapers.errors import InvalidQueryError

class ConnecticutCivil(SeleniumBase):

    BASE_URL = "http://civilinquiry.jud.ct.gov/CourtEventsSearchByDate.aspx"

    def _validate_date(self, date_type):
        super()._validate_date(date_type)
        if date_type < datetime.date.today():
            raise InvalidQueryError("The date you enter must occur today or in the future")

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
        if not isinstance(case_date, datetime.date):
            raise TypeError("The parameter of get_court_cases must be a valid date (i.e. datetime.date object)")
        if datetime.date.today() > case_date:
            raise InvalidQueryError("The date you enter needs to be on today's date or in the future")
        # TODO: Finish this
