from auth import E3DBAuth

class Client:
    def __init__(self, config):
        self.api_url = config['api_url']
        self.api_key_id = config['api_key_id']
        self.api_secret = config['api_secret']
        self.client_id = config['client_id']
        self.client_email = config['client_email']
        self.public_key = config['public_key']
        self.private_key = config['private_key']
        self.e3db_auth = E3DBAuth(self.api_key_id, self.api_secret, self.api_url)

    def do_test(self):
        import requests
        r = requests.get(self.api_url + '/v1/storage/foobar', auth=self.e3db_auth)
        print r.status_code
