import json
import os

class Config:

    DEFAULT_API_URL = "https://api.e3db.com"
    def __init__(self, client_id, api_key_id, api_secret, public_key, private_key, client_email="", version="1", api_url=DEFAULT_API_URL, logging=False):
        self.version = version
        self.client_id = client_id
        self.api_key_id = api_key_id
        self.api_secret = api_secret
        self.client_email = client_email
        self.public_key = public_key
        self.private_key = private_key
        self.api_url = api_url
        self.logging = logging

    def __call__(self):
        # returns dict of config
        return {
            'version': self.version,
            'client_id': self.client_id,
            'api_key_id': self.api_key_id,
            'api_secret': self.api_secret,
            'client_email': self.client_email,
            'public_key': self.public_key,
            'private_key': self.private_key,
            'api_url': self.api_url,
            'logging': self.logging
        }

    @classmethod
    def __load_file(self, filename):
        '''
        Reads file from disk, and returns the json object as a dict
        '''
        try:
            with open(filename) as e3db_config:
                data = json.load(e3db_config)
            return data
        except ValueError as error:
            print "Loading E3DB json file failed. Perhaps the JSON is malformed?"
            print "Error: " + str(error)
            
    @classmethod
    def load(self, profile=''):
        # if profile is empty we read the default ~/.tozny/e3db.json file
        home = os.path.expanduser('~')
        return Config.__load_file(os.path.join(home, '.tozny',  profile, 'e3db.json'))
