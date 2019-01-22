
class Range():
    def __init__(self, key="CREATED", format="Unix", zone="UTC", zone_offset=None, before=None, after=None):
        '''
        before, after are naive datetime objects

        '''
        self.__key= key
        self.__format = format
        self.__zone = zone
        self.__before = before 
        self.__after = after
        if zone_offset is not None:
            self.__zone_offset = zone_offset
        else:
            zone_dict = {
                "PST":"-08:00",
                "MST":"-07:00",
                "CST":"-06:00",
                "EST":"-05:00",
                "UTC":"+00:00"
            } 
            self.__zone_offset = zone_dict.get(zone, "+00:00")
    
    @property
    def before(self):
        return self.__before.isoformat("T") + self.__zone_offset

    @property
    def after(self):
        return self.__after.isoformat("T") + self.__zone_offset

    def to_json(self):
        return {
            "range_key": str(self.__key),
            "before": self.__before.isoformat("T") + self.__zone_offset,
            "after": self.__after.isoformat("T") + self.__zone_offset
        }
