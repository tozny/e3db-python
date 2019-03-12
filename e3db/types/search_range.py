from datetime import timezone, timedelta, datetime
import re

class Range():
    def __init__(self, key="CREATED", start=None, end=None, zone_offset=None):
        """
        Initialize the Range class for use in Search. This class can be manually created if needed, but 
        the Search.range() method handles the Search workflow.

        Once created, modifying zone_offset will not propogate the timezone changes over to start and end.
        If you wish to change the zone for a particular time within the same Range object, provide a datetime object
        with zone information (tzinfo).

        Parameters
        ----------
        key : str, optional
            "CREATED|MODIFIED" (the default is "CREATED")

        start: datetime, int, optional
            Search only for records that come after this time.
            Accepts datetime object with and without timezone information, see zone_offset for more details.
            OR
            Accepts int denoting unix epoch seconds.
            (the default is None, which leaves no lower bound on the query)
        
        end : datetime, int, optional
            Search only for records that come before this time 
            Accepts datetime object with and without timezone information, see zone_offset for more details.
            OR
            Accepts int denoting unix epoch seconds.
            (the default is None, which leaves no upper bound on the query)

        zone_offset : int, str, optional
            Accepts int for provided timezone in hour difference from UTC.
            For PST(UTC-8) provide zone_offset = -8
            For PDT(UTC-7) provide zone_offset = -7
            and so on for valid UTC offsets...
            For a more comprehensive list see https://en.wikipedia.org/wiki/List_of_UTC_time_offsets

            If datetime object has timezone information, that will be given precedence.
            If zone_offset is provided, datetime objects, start and end append this timezone
                ex:
                    - input: zone_offset = -7, datetime.isoformat("T") = 2019-01-01T00:00:00Z
                    - output: 2019-01-01T00:00:00Z-07:00
                This option should only be used if you know you want to search 
                for a specific time within a different timezone.
            If zone_offset == None and tzinfo does not exist, UTC will be used by default.
            Assumes that start and end have the same timezone information
        
        Returns
        ----------
        None
        """
        self.__key = key
        self.zone_offset = zone_offset
        self.start = start
        self.end = end

    @staticmethod
    def _set_timezone(t, zone_offset_minutes=None):
        """
        Parameters
        ----------
        t : datetime
            datetime that may need timezone information

        zone_offset: int, optional
            number denoting the offset in hours from utc

        Returns
        -------
        datetime
            datetime with proper timezone information
        """
        if t.tzinfo is not None:
            return t
        if zone_offset_minutes is not None:
            return t.replace(tzinfo=timezone(timedelta(minutes=zone_offset_minutes)))
        return t.replace(tzinfo=timezone(timedelta(hours=0)))

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
        self.__end = t
        if t is not None:
            if isinstance(t, int):
                utc_no_timezone = datetime.utcfromtimestamp(t)
                utc = utc_no_timezone.replace(tzinfo=timezone(timedelta(minutes=0)))
                self.__end = utc
            elif isinstance(t, datetime):
                self.__end = t
                self.__end = Range._set_timezone(t, self.__zone_offset_minutes)
            else:
                raise TypeError('end time only accepts types int or datetime')

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
        self.__start = t
        if t is not None:
            if isinstance(t, int):
                utc_no_timezone = datetime.utcfromtimestamp(t)
                utc = utc_no_timezone.replace(tzinfo=timezone(timedelta(minutes=0)))
                self.__start = utc
            elif isinstance(t, datetime):
                self.__start = t
                self.__start = Range._set_timezone(t, self.__zone_offset_minutes)
            else:
                raise TypeError('start time only accepts types int or datetime')

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
            and so on for valid UTC offsets...
            For a more comprehensive list see https://en.wikipedia.org/wiki/List_of_UTC_time_offsets

        Returns
        -------
        None
        """
        self.__zone_offset = z
        self.__zone_offset_minutes = None
        if z is not None:
            if isinstance(z, int):
                self.__zone_offset_minutes = z * 60
            elif isinstance(z, str):
                confirm_format = r'^[+|-]\d{2}:\d{2}$'
                if re.search(confirm_format, z) is None:
                    raise TypeError('a zone offset string must be in the in the format "[+|-]HH:MM"')

                time_information = [int(s) for s in re.findall(r'\d+', z)]
                self.__zone_offset_minutes = (time_information[0] * 60) + time_information[1]

                if z[0] == '-':
                    self.__zone_offset_minutes = self.__zone_offset_minutes * -1 
            else:
                raise TypeError('zone offset only accepts an int, denoting hours offset, or a str in the format "+HH:MM" ')
    
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
