class ConflictError(Exception):
    def __init__(self, record_id):
        Exception.__init__(self, "Conflict updating record: {0}".format(record_id))

class QueryError(Exception):
    def __init__(self, record_id):
        Exception.__init__(self, "Error during query: {0}".format(record_id))

class LookupError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during lookup: {0}".format(text))
