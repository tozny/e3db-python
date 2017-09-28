import e3db
from e3db.auth import E3DBAuth
import requests

conf = e3db.Config()
conf_dict = conf.load('dev')

# only created once
e3db_auth = E3DBAuth(conf_dict['api_key_id'], conf_dict['api_secret'], api_url=conf_dict['api_url'])
r = requests.get("https://dev.e3db.com/v1/storage/foobar", auth=e3db_auth)
print r.status_code
