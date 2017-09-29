from auth import E3DBAuth
from crypto import Crypto
from config import Config
import requests

class PublicKey():
    def __init__(self, key_type, public_key):
        self.key_type = str(key_type)
        self.public_key = str(public_key)

    def json_serialize(self):
        return {self.key_type: self.public_key}

    def get_pubkey(self):
        return self.public_key

class Record():
    def __init__(self, meta, data):
        self.meta = meta
        self.data = data
    def json_serialize(self):
        return {
            'meta': self.meta,
            'data': self.data
        }

class Meta():
    def __init__(self, record_id, writer_id, user_id, record_type, plain, created, last_modified, version):
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
            'record_type': self.record_type,
            'plain': self.plain,
            'created': self.created,
            'last_modified': self.last_modified,
            'version': self.version
        }

class Client:
    DEFAULT_QUERY_COUNT = 100
    DEFAULT_API_URL = "https://api.e3db.com"

    def __init__(self, config):
        self.api_url = config['api_url']
        self.api_key_id = config['api_key_id']
        self.api_secret = config['api_secret']
        self.client_id = config['client_id']
        self.client_email = config['client_email']
        self.public_key = config['public_key']
        self.private_key = config['private_key']
        self.e3db_auth = E3DBAuth(self.api_key_id, self.api_secret, self.api_url)

    def debug(self):
        import pdb; pdb.set_trace()

    def __decrypt_record(self, record):
        pass

    def __decrypt_record_with_key(self, record):
        pass

    def __encrypt_record(self, plaintext_record):
        pass

    def __decrypt_eak(self, json):
        pass

    def __get_access_key(self, writer_id, user_id, reader_id, type):
        pass

    def __put_access_key(self, writer_id, user_id, reader_id, type, ak):
        pass

    def __delete_access_key(self, writer_id, user_id, reader_id, type):
        pass


    @classmethod
    def register(self, registration_token, client_name, wrapped_public_key, api_url=DEFAULT_API_URL, private_key=None, backup=False):
        # TODO support backup
        url = "{0}/{1}/{2}/{3}/{4}/{5}".format(api_url, 'v1', 'account', 'e3db', 'clients', 'register')
        payload = {
            'token': registration_token,
            'client': {
                'name': client_name,
                'public_key': wrapped_public_key.json_serialize()
            }
        }
        response = requests.post(url=url, json=payload)
        client_info = response.json()
        backup_client_id = response.headers['x-backup-client']

        if backup == True:
            if private_key == None:
                raise RuntimeError, "Cannot back up client credentials without a private key!"
            else:
                config = Config('1',
                    client_info['client_id'], \
                    client_info['api_key_id'], \
                    client_info['api_secret'], \
                    '', \
                    wrapped_public_key, \
                    private_key, \
                    api_url=api_url \
                    )

                client = Client(config())

                client.backup(backup_client_id, registration_token)

        #if response.status_code != 201
        return client_info

    @classmethod
    def generate_keypair(self):
        public_key, private_key = Crypto.generate_keypair()
        return Crypto.encode_public_key(public_key), Crypto.encode_private_key(private_key)

    def client_info(self, client_id):
        pass

    def client_key(self, client_id):
        pass

    def read_raw(self, record_id):
        pass

    def read(self, record_id):
        pass

    def write(self, type, data, plain):
        pass

    def update(self, record):
        pass

    def delete(self, record_id):
        pass

    def backup(self, client_id, registration_token):
        credentials = {
            'version': '1',
            'client_id': self.client_id,
            'api_key_id': self.api_key_id,
            'api_secret': self.api_secret,
            'client_email': self.client_email,
            'public_key': self.public_key.get_pubkey(),
            'private_key': self.private_key,
            'api_url': self.api_url
        }

        self.write('tozny.key_backup', credentials, {'client': self.client_id})
        # share this record type with the backup client
        self.share('tozny.key_backup', client_id)

        url = self.get_url('v1', 'account', 'backup', registration_token, self.client_id)
        requests.post(url=url, auth=self.e3db_auth)

    def query(self, data=True, raw=False, writer=None, record=None, type=None, plain=None, page_size=DEFAULT_QUERY_COUNT):
        pass

    def share(self, type, reader_id):
        pass

    def revoke(self, type, reader_id):
        pass

    def outgoing_sharing(self):
        pass

    def incoming_sharing(self):
        pass

    def get_url(self, *args):
        # list of paths that we make a nice url from
        return self.api_url + '/' + '/'.join(args)
