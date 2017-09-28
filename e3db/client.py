from auth import E3DBAuth
from crypto import Crypto

class Client:
    DEFAULT_QUERY_COUNT = 100

    def __init__(self, config):
        self.api_url = config['api_url']
        self.api_key_id = config['api_key_id']
        self.api_secret = config['api_secret']
        self.client_id = config['client_id']
        self.client_email = config['client_email']
        self.public_key = config['public_key']
        self.private_key = config['private_key']
        self.e3db_auth = E3DBAuth(self.api_key_id, self.api_secret, self.api_url)
        self.crypto = Crypto()

    def do_test(self):
        import requests
        r = requests.get(self.get_url('v1','storage','stuff'), auth=self.e3db_auth)
        print r.status_code

    @classmethod
    def register(self, registration_token, client_name, public_key, private_key=None, backup=False):
        # self.api_url
        pass

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
        pass

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
