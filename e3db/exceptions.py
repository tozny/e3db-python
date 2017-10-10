class QueryError(Exception):
    def __init__(self, record_id):
        Exception.__init__(self, "Error during query: {0}".format(record_id))

class LookupError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during lookup: {0}".format(text))

class EAKError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during EAK operation: {0}".format(text))

class CryptoError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during Crypto operation: {0}".format(text))

class APIError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during API operation: {0}".format(text))
