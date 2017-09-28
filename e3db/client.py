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
        r = requests.get(self.get_url('v1','auth','storage'), auth=self.e3db_auth)
        print r.status_code

    def register(registration_token, client_name, public_key, private_key=None, backup=False):
        # self.api_url
        pass


    def client_info(client_id):
        pass

    def client_key(client_id):
        pass

    def read_raw(record_id):
        pass

    def read(record_id):
        pass

    def write(type, data, plain):
        pass

    def update(record):
        pass

    def delete(record_id):
        pass

    def backup(client_id, registration_token):
        pass

    def query(data=True, raw=False, writer=None, record=None, type=None, plain=None, page_size=DEFAULT_QUERY_COUNT):
        pass

    def share(type, reader_id):
        pass

    def revoke(type, reader_id):
        pass

    def outgoing_sharing():
        pass

    def incoming_sharing():
        pass

    def get_url(*args):
        # list of paths that we make a nice url from
        return self.api_url + '/' + '/'.join(args)
