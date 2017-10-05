# types.py

class IncomingSharingPolicy():
    def __init__(self, json):
        self.writer_id = json['writer_id']
        self.writer_name = json['writer_name']
        self.record_type = json['record_type']

    def json_serialize(self):
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

    def json_serialize(self):
        return {
            'reader_id': self.reader_id,
            'reader_name': self.reader_name,
            'record_type': self.record_type
        }

class PublicKey():
    # TODO not used, remove?
    def __init__(self, key_type, public_key):
        self.key_type = str(key_type)
        self.public_key = str(public_key)

    def json_serialize(self):
        return {self.key_type: self.public_key}

    def get_pubkey(self):
        return self.public_key

class Record():
    def __init__(self, meta=None, data=None):
        self.meta = meta
        self.data = data

    def json_serialize(self):
        return {
            'meta': self.meta.json_serialize(),
            'data': self.data
        }

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
    def json_serialize(self):
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

    def json_serialize(self):
        return {
            'client_id': self.client_id,
            'public_key': self.public_key,
            'validated': self.validated
        }
