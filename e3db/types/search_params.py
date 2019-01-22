import uuid

class Params():
    def __init__(self, condition="OR", strategy="EXACT", keys=None, values=None, writer_ids=None, user_ids=None, record_ids=None, content_types=None, plain={}):
        # python3 is picky about uuids, cant pass a uuid to uuid.UUID
        self.__condition = condition
        self.__strategy = strategy
        self.__writer_ids = [i if isinstance(i, uuid.UUID) else uuid.UUID(i) for i in user_ids]
        self.__user_ids = [i if isinstance(i, uuid.UUID) else uuid.UUID(i) for i in user_ids]
        self.__record_ids = [i if isinstance(i, uuid.UUID) else uuid.UUID(i) for i in user_ids]
        self.__content_types = [str(i) for i in content_types]
        self.__plain = dict(plain) if plain is not None else None
        self.__values = [str(i) for i in values]
        self.__keys = [str(i) for i in keys]

    def to_json(self):
        return {
            "condition": self.__condition,
            "strategy": self.__strategy,
            "terms": {
                "writer_ids": [str(i) for i in self.__writer_ids],
                "user_ids": [str(i) for i in self.__user_ids],
                "record_ids": [str(i) for i in self.__record_ids],
                "content_types": [str(i) for i in self.__content_types],
                "keys": [str(i) for i in self.__keys],
                "values": [str(i) for i in self.__values],
                "tags": self.__plain
            }
        }