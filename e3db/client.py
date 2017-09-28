import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import datetime

class E3DBAuth(AuthBase):
    def __init__(self, api_key_id, api_secret, api_url="https://api.e3db.com"):
        self.api_key_id = api_key_id
        self.api_secret = api_secret
        self.api_url = api_url
        self.token = None
        # guaranteed to be less than current time (Unix Epoch)
        self.expires_at = datetime.datetime(1970, 1, 1)

    def __call__(self, r):
        # modify and return the request
        # check if the E3DB token header already exists and is not expired
        # 'cuz UTC
        # if we need to renew the token for the request, we do that real quick.
        if (self.token == None) or (datetime.datetime.utcnow() > self.expires_at):
            grant = {'grant_type': 'client_credentials'}
            refresh_request = requests.post(url="{0}/v1/auth/token".format(self.api_url), auth=HTTPBasicAuth(self.api_key_id, self.api_secret), data=grant)
            refresh_json = refresh_request.json()
            self.token = refresh_json['access_token']
            expire_time = refresh_json['expires_at']
            # now save that as a datetime object so we can do later comparison
            self.expires_at = datetime.datetime.strptime(expire_time, "%Y-%m-%dT%H:%M:%S.%fZ" )
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r
