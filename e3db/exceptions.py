class ConflictError(Exception):
    def __init__(self, record_id):
        Exception.__init__(self, "Conflict updating record: {0}".format(record_id))
