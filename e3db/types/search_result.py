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

        after_index : int
            Index that indicates where to start the next query for batch jobs.

        search_id : str
            ID to access search_id for async searches, but currently is not implemented in
            the search service.  

        Returns
        -------
        SearchResult
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
        """
        Get search_id for SearchResult
        
        Returns
        -------
        str
            ID to access search_id for async searches, but currently is not implemented in
            the search service.  
        """
        return self.__search_id
    
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

    @property
    def records(self):
        """
        Get records for SearchResult
        
        Returns
        -------
        Record
            Returns Records for manual access
        """
        return self.__records

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
