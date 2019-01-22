from .search import Search
from .record import Record

class SearchResult(object):

    def __init__(self, search, records, after_index=0, search_id=""):
        """
        Initialize the SearchResult class.

        This object type is used as a storage for the results of v2 Search query.
        The main purpose is to allow iteration over a list of returned records
        that are the result of a Search operation.

        Parameters
        ----------
        search : e3db.Search
            Search object stored for later operations, such as looking up the
            after index returned from the server during search execution.

        records : list<e3db.Record>
            A list of records to store for later iteration and operations.

        Returns
        -------
        None
        """
        if search and (not isinstance(search, Search)):
            raise TypeError("Search object is not e3db.Search type. Given type: {0}".format(type(search)))
        else:
            self.__search = search

        # Check that all records in this list are of type e3db.Record
        if records and (not all(isinstance(x, Record) for x in records)):
            raise TypeError("Records should be a list of e3db.Record types. Given type: {0}".format(type(records)))
        else:
            self.__records = records
        self.__after_index = after_index
        self.__search_id = search_id

    @property
    def search_id(self):
        return self.__search_id
    
    @search_id.setter
    def search_id(self, id):
        self.__search_id = id

    # after_index getters and setters
    @property
    def after_index(self):
        """
        Get after_index of Search.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Get after_index of the Search.
        """
        return self.__after_index

    @after_index.setter
    def after_index(self, value):
        """
        Set after_index of SearchResult

        Parameters
        ----------
        value: int
            Set after_index from server result

        Returns
        -------
        None
        """
        self.__after_index = int(value)

    def __iter__(self):
        """
        Iterate over record objects.

        Parameters
        ----------
        None

        Returns
        -------
        iter
            Iterator over record objects returned from the Search.
        """

        return iter(self.__records)

    def __len__(self):
        """
        Get amount of records returned from the Search.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Amount of records returned from the Search.
        """

        return len(self.__records)
