from datetime import timezone, timedelta

class Range():
    def __init__(self, key="CREATED", start=None, end=None, zone_offset=None):
        """
        Initialize the Range class for use in Search. This class can be manually created if needed, but 
        the Search.range() method handles the Search workflow.

        Parameters
        ----------
        key : str, optional
            "CREATED|MODIFIED" (the default is "CREATED")

        start: time, optional
            Search only for record that come after this time 
            (the default is None, which leaves no lower bound on the query)
        
        end : time, optional
            Search only for records that come before this time 
            (the default is None, which leaves no upper bound on the query)

        zone_offset : int, optional
            Accepts int for provided timezone in hour difference from UTC.
            For PST(UTC-8) provide zone_offset = -8
            For PDT(UTC-7) provide zone_offset = -7

            If datetime object has timezone information, that will be given precedence.
            If zone_offset is provided, datetime objects, start and end append this timezone
                ex:
                    - input: zone_offset = -7, datetime.isoformat("T") = 2019-01-01T00:00:00Z
                    - output: 2019-01-01T00:00:00Z-07:00
                This option should only be used if you know you want to search 
                for a specific time within a different timezone.
            If zone_offset == None and tzinfo does not exist, your local timezone will be used.
            Assumes that start and end have the same timezone information
        
        Returns
        ----------
        None
        """
        self.__key = key
        self.__start = start 
        self.__end = end
        self.__zone_offset = zone_offset

        if start is not None:
            self.__start = Range._set_timezone(start, zone_offset)
        if end is not None:
            self.__end = Range._set_timezone(end, zone_offset)

    @staticmethod
    def _set_timezone(t, zone_offset=None):
        """
        If datetime object has timezone information, that will be given precedence.
        If zone_offset is provided, datetime objects, start and end append this timezone
            ex:
                - input: zone_offset = -7, datetime.isoformat("T") = 2019-01-01T00:00:00Z
                - output: 2019-01-01T00:00:00Z-07:00
            This option should only be used if you know you want to search 
            for a specific time within a different timezone.
        If zone_offset == None and tzinfo does not exist, your local timezone will be used.
        Assumes that start and end have the same timezone information

        Parameters
        ----------
        t : datetime
            datetime that needs timezone information

        zone_offset: int, optional
            number denoting the offset in hours from utc

        Returns
        -------
        datetime
            datetime with proper timezone information
        """
        if t.tzinfo is not None:
            return t
        if zone_offset is not None:
            return t.replace(tzinfo=timezone(timedelta(hours=zone_offset)))
        return t.astimezone()

    @property
    def end(self):
        """
        Get the end time as datetime object

        Returns
        -------
        datetime
            end time for query.
        """
        return self.__end
    
    def end_formatted(self):
        """
        Get the end time with time zone information appended as a string

        Returns
        -------
        str
            end time properly formatted to send to E3DB.
        """
        if self.__end is None:
            return None
        return self.__end.isoformat("T")

    @end.setter
    def end(self, t):
        """
        Set the end time of Search Range

        Parameters
        ----------
        t : datetime
            upper time bound for Search Range

        Returns
        -------
        None
        """
        if t is not None:
            t = Range._set_timezone(t, self.__zone_offset) 
        self.__end = t

    @property
    def start(self):
        """
        Get the start time as datetime object

        Returns
        -------
        datetime
            start time for query.
        """
        return self.__start

    def start_formatted(self):
        """
        Get the start time with time zone information appended as a string

        Returns
        -------
        str
            start time properly formatted to send to E3DB.
        """
        if self.__start is None:
            return None
        return self.__start.isoformat("T")

    @start.setter
    def start(self, t):
        """
        Set the start time of Search Range

        Parameters
        ----------
        t : datetime
            lower time bound for Search Range

        Returns
        -------
        None
        """
        if t is not None:
            t = Range._set_timezone(t, self.__zone_offset) 
        self.__start = t

    @property
    def zone_offset(self):
        """
        Get zone_offset of Search Range
        
        Returns
        -------
        int
            zone_offset value
        """
        return self.__zone_offset

    @zone_offset.setter
    def zone_offset(self, z):
        """
        Set zone_offset for Search Range
        Updates start and end time to match the newly set zone IFF they are timezone naive.

        Parameters
        ----------
        z : int
            Accepts int for provided timezone in hour difference from UTC.
            For PST(UTC-8) provide zone_offset = -8
            For PDT(UTC-7) provide zone_offset = -7

        Returns
        -------
        None
        """
        self.__zone_offset = z
        if self.__start is not None:
            self.__start = Range._set_timezone(self.__start, z)
        if self.__end is not None:
            self.__end = Range._set_timezone(self.__end, z)
    
    @property
    def key(self):
        """
        Get Key for Search Range
        
        Returns
        -------
        str
            "CREATED|MODIFIED"
        """
        return self.__key

    @key.setter
    def key(self, k):
        """
        Set Key for Search Range

        Parameters
        ----------
        k : str
            Valid keys: "CREATED|MODIFIED"

        Returns
        -------
        None
        """
        self.__key = k

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.
        
        Returns
        -------
        dict
            JSON-style document containing the Range elements.
        """
        to_serialize = {
            "range_key": str(self.__key),
            "before": self.end_formatted(),
            "after": self.start_formatted(),
        }
        # remove None (JSON null) objects
        for key, value in list(to_serialize.items()):
            if value is None or value == 'None':
                del to_serialize[key]

        return to_serialize