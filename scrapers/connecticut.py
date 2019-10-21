import datetime
from base_scrapers import SeleniumBase
from errors import InvalidQueryError

class ConnecticutCivil(SeleniumBase):

    def __init__(self, exec_path=None):
        super(SeleniumBase, self).__init__(exec_path=exec_path)

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
