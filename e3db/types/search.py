import time
from .search_range import Range
from .search_params import Params

class Search(object):
    def __init__(self, last_index=0, count=50, include_all_writers=False, include_data=False, match=None, exclude=None, range=None): 
        """
        Initialize the search v2 class.

        This object type is used to build a v2/search query to run against the server.
        It is exposed through the e3db.Client.search method.

        Parameters
        """
        self.__next_token = int(last_index)
        self.__limit = int(count)
        self.__include_data = bool(include_data)
        self.__include_all_writers = bool(include_all_writers)
        self.__match = match if match else [] 
        self.__exclude = exclude if exclude else []
        self.__range = None
        
    def append_match(self, p):
        self.__match.append(p)

    def append_exclude(self, p):
        self.__exclude.append(p)

    # count getters
    @property
    def count(self):
        """
        Get count of Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get count of records.
        """
        return self.__limit

    # after_index getters
    @property
    def after_index(self):
        """
        Get after_index of Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get after_index of the Query.
        """
        return self.__next_token

    @after_index.setter
    def after_index(self, value):
        """
        Set after_index of QueryResult

        Parameters
        ----------
        value: int
            Set after_index from server result

        Returns
        -------
        None
        """
        self.__next_token = int(value)

    # include_data getters
    @property
    def include_data(self):
        """
        Get included_data of Query.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            Whether data is included with the records.
        """
        return self.__include_data


    # include_all_writers getters
    @property
    def include_all_writers(self):
        """
        Get whether the query included all writers.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            include_all_writers
        """
        return self.__include_all_writers

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Query elements.
        """
        return {
            "limit": int(self.__limit),
            "next_token": int(self.__next_token),
            "include_all_writers": bool(self.__include_all_writers),
            "include_data": bool(self.__include_data),
            "match": [i.to_json() for i in self.__match],
            "exclude": [i.to_json() for i in self.__exclude],
            "range": self.__range.to_json() if self.__range is not None else {}
        }

    def match(self, condition="OR", strategy="EXACT", writer=[], record=[], user=[], record_type=[], keys=[], values=[], plain=None):
        m = Params(condition=condition, strategy=strategy, writer_ids=writer, record_ids=record, user_ids=user, content_types=record_type, keys=keys, values=values, plain=plain)
        self.append_match(m)
        return self

    def exclude(self, condition="OR", strategy="EXACT", writer=[], record=[], user=[], record_type=[], keys=[], values=[], plain=None):
        e = Params(condition=condition, strategy=strategy, writer_ids=writer, record_ids=record, user_ids=user, content_types=record_type, keys=keys, values=values, plain=plain)
        self.append_exclude(e)
        return self
    
    def range(self, key="CREATED", format="Unix", zone="UTC", before=None, after=None):
        r = Range(key=key, format=format, zone=zone, before=before, after=after)
        self.__range = r
        return self
