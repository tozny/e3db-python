# types.py

class IncomingSharingPolicy():
    def __init__(self, json):
        self.writer_id = json['writer_id']
        self.writer_name = json['writer_name']
        self.record_type = json['record_type']

    def to_json(self):
        return {
            'writer_id': self.writer_id,
            'writer_name': self.writer_name,
            'record_type': self.record_type
        }

class OutgoingSharingPolicy():
    def __init__(self, json):
        self.reader_id = json['reader_id']
        self.reader_name = json['reader_name']
        self.record_type = json['record_type']

    def to_json(self):
        return {
            'reader_id': self.reader_id,
            'reader_name': self.reader_name,
            'record_type': self.record_type
        }

class Record():
    def __init__(self, meta=None, data=None):
        self.meta = meta
        self.data = data

    def to_json(self):
        return {
            'meta': self.meta.to_json(),
            'data': self.data
        }

    def get_meta(self):
        return self.meta

    def get_data(self):
        return self.get_data

    def update_meta(self, meta):
        self.meta = meta

    def update(self, meta, data):
        self.meta.update(meta)
        self.data = data

class Meta():
    def __init__(self, record_id=None, writer_id=None, user_id=None, \
        record_type=None, plain=None, created=None, last_modified=None, \
        version=None):
        self.record_id = record_id
        self.writer_id = writer_id
        self.user_id = user_id
        self.record_type = record_type
        self.plain = plain
        self.created = created
        self.last_modified = last_modified
        self.version = version
    def to_json(self):
        return {
            'record_id': self.record_id,
            'writer_id': self.writer_id,
            'user_id': self.user_id,
            'type': self.record_type,
            'plain': self.plain,
            'created': self.created,
            'last_modified': self.last_modified,
            'version': self.version
        }
    def update(self, json):
        self.record_id = json['record_id']
        self.writer_id = json['writer_id']
        self.user_id = json['user_id']
        self.record_type = json['type']
        self.plain = json['plain']
        self.created = json['created']
        self.last_modified = json['last_modified']
        self.version = json['version']

class ClientInfo():
    def __init__(self, client_id, public_key, validated):
        self.client_id = str(client_id)
        self.public_key = public_key
        self.validated = validated

    def to_json(self):
        return {
            'client_id': self.client_id,
            'public_key': self.public_key,
            'validated': self.validated
        }

class ClientDetails():
    def __init__(self, json):
        self.client_id = json['client_id']
        self.api_key_id = json['api_key_id']
        self.api_secret = json['api_secret']
        self.public_key = json['public_key']
        self.name = json['name']

    def to_json(self):
        return {
            'client_id': self.client_id,
            'api_key_id': self.api_key_id,
            'api_secret': self.api_secret,
            'public_key': self.public_key,
            'name': self.name
        }

    def get_api_credentials(self):
        return (self.api_key_id, self.api_secret)

    def get_client_id(self):
        return self.client_id

class QueryResult():

    def __init__(self, query, records):
        self.query = query
        self.records = records

    def __iter__(self):
        return iter(self.records)

    def next(self):
        raise StopIteration
        pass

class Query():

    def __init__(self, count, after_index=0, include_data=False, \
        writer_ids=None, user_ids=None, record_ids=None, content_types=None, \
        plain={}, include_all_writers=False):
        self.count = count
        self.after_index = after_index
        self.include_data = include_data
        self.writer_ids = writer_ids
        self.user_ids = user_ids
        self.record_ids = record_ids
        self.content_types = content_types
        self.plain = plain
        self.include_all_writers = include_all_writers

    def to_json(self):
        return {
            'count': self.count,
            'after_index': self.after_index,
            'include_data': self.include_data,
            'writer_ids': self.writer_ids,
            'user_ids': self.user_ids,
            'record_ids': self.record_ids,
            'content_types': self.content_types,
            'plain': self.plain,
            'include_all_writers': self.include_all_writers
        }
