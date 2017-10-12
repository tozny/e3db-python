from auth import E3DBAuth
from crypto import Crypto
from config import Config
from types import *
from exceptions import *
import requests
import urllib

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

    @classmethod
    def __response_check(self, response):
        '''
        Takes in requests.models.Response object, and determines if there was
        and error with the request. If there was an error, we raise an error
        with the APIError exception and a message detailing the error.
        Does not return anything.
        '''
        # Map of HTTP error codes to exception messages
        errors = {
            401: 'Unauthenticated: HTTP 401',
            403: 'Unauthorized: HTTP 403',
            404: 'Requested item not found: HTTP 404',
            409: 'Existing item cannot be modified: HTTP 409'
        }

        if response.status_code in errors:
            raise APIError(errors[response.status_code])

    def __decrypt_record(self, record):
        meta = record.to_json()['meta']
        writer_id = meta['writer_id']
        user_id = meta['user_id']
        record_type = meta['type']
        ak = self.__get_access_key(writer_id, user_id, self.client_id, record_type)
        return self.__decrypt_record_with_key(record, ak)

    def __decrypt_record_with_key(self, record, ak):
        encrypted_record = record.to_json()

        for key,value in encrypted_record['data'].iteritems():
            fields = value.split(".")

            if len(fields) != 4:
                raise CryptoError("Invalid Encrypted record fields: {0}".format(value))

            edk = Crypto.base64decode(fields[0])
            edkN = Crypto.base64decode(fields[1])
            ef = Crypto.base64decode(fields[2])
            efN = Crypto.base64decode(fields[3])

            dk = Crypto.decrypt_secret(ak, edk, edkN)
            pv = Crypto.decrypt_secret(dk, ef, efN)

            encrypted_record['data'][key] = pv
        # return new Record object data with plaintext data
        return Record(Meta(encrypted_record['meta']), encrypted_record['data'])

    def __encrypt_record(self, plaintext_record):
        record = plaintext_record.to_json()

        meta = record['meta']
        writer_id = meta['writer_id']
        user_id = meta['user_id']
        record_type = meta['type']

        ak = self.__get_access_key(writer_id, user_id, self.client_id, record_type)

        # if the ak is missing, we need to create and push one to the server.
        if ak == None:
            ak = Crypto.random_key()
            self.__put_access_key(writer_id, user_id, self.client_id, record_type, ak)

        # Loop through the plaintext fields and encrypt them
        for key, value in record['data'].iteritems():
            dk = Crypto.random_key()
            efN = Crypto.random_nonce()
            ef = Crypto.encrypt_secret(dk, str(value), efN)
            ef = ef[len(efN):] # remove nonce from ciphertext
            edkN = Crypto.random_nonce()
            edk = Crypto.encrypt_secret(ak, dk, edkN)
            edk = edk[len(edkN):] # remove nonce from ciphertext

            record['data'][key] = ".".join([Crypto.base64encode(c) for c in [edk, edkN, ef, efN]])

        # return new Record object data with encrypted data
        return Record(Meta(meta), record['data'])

    def __decrypt_eak(self, eak_json):
        k = eak_json['authorizer_public_key']['curve25519']
        authorizer_pubkey = Crypto.decode_public_key(k)
        fields = eak_json['eak'].split('.')
        if len(fields) != 2:
            raise CryptoError("Invalid access key format: {0}".format(eak_json['eak']))
        ciphertext = Crypto.base64decode(fields[0])
        nonce = Crypto.base64decode(fields[1])
        return Crypto.decrypt_eak(Crypto.decode_private_key(self.private_key), authorizer_pubkey, ciphertext, nonce)

    def __get_access_key(self, writer_id, user_id, reader_id, record_type):
        url = self.__get_url("v1", "storage", "access_keys", writer_id, user_id, reader_id, record_type)
        response = requests.get(url=url, auth=self.e3db_auth)
        # return None if eak not found, otherwise return eak
        if response.status_code == 404:
            return None
        else:
            self.__response_check(response)
            json = response.json()
            return self.__decrypt_eak(json)

    def __put_access_key(self, writer_id, user_id, reader_id, record_type, ak):
        reader_key = self.__client_key(reader_id)
        nonce = Crypto.random_nonce()
        eak = Crypto.encrypt_ak(Crypto.decode_private_key(self.private_key), reader_key, ak, nonce)
        # Need to strip the nonce off the front of the eak
        eak = eak[len(nonce):]
        encoded_eak = "{0}.{1}".format(Crypto.base64encode(eak), Crypto.base64encode(nonce))
        url = self.__get_url("v1", "storage", "access_keys", writer_id, user_id, reader_id, record_type)
        json = {
            'eak': encoded_eak
        }
        response = requests.put(url=url, json=json, auth=self.e3db_auth)
        self.__response_check(response)

    def __delete_access_key(self, writer_id, user_id, reader_id, record_type):
        url = self.__get_url("v1", "storage", "access_keys", writer_id, user_id, reader_id, record_type)
        requests.delete(url=url, auth=self.e3db_auth)

    def outgoing_sharing(self):
        url = self.__get_url("v1", "storage", "policy", "outgoing")
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        # create list of policy objects, and return them
        policies = []
        # check if there are no policies
        if response.json():
            for policy in response.json():
                policies.append(OutgoingSharingPolicy(policy))
        return policies

    def incoming_sharing(self):
        url = self.__get_url("v1", "storage", "policy", "incoming")
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        # create list of policy objects, and return them
        policies = []
        # check if there are no policies
        if response.json():
            for policy in response.json():
                policies.append(IncomingSharingPolicy(policy))
        return policies

    def __get_url(self, *args):
        # list of paths that we make a nice url from
        return self.api_url + '/' + '/'.join(args)

    @classmethod
    def register(self, registration_token, client_name, public_key, private_key=None, backup=False, api_url=DEFAULT_API_URL):
        url = "{0}/{1}/{2}/{3}/{4}/{5}".format(api_url, 'v1', 'account', 'e3db', 'clients', 'register')
        payload = {
            'token': registration_token,
            'client': {
                'name': client_name,
                'public_key': {
                    'curve25519': public_key
                }
            }
        }
        response = requests.post(url=url, json=payload)
        self.__response_check(response)
        client_info = response.json()
        backup_client_id = response.headers['x-backup-client']

        if backup:
            if private_key == None:
                raise RuntimeError, "Cannot back up client credentials without a private key!"

            config = Config(
                client_info['client_id'], \
                client_info['api_key_id'], \
                client_info['api_secret'], \
                public_key, \
                private_key, \
                api_url=api_url \
                )

            client = Client(config())
            client.backup(backup_client_id, registration_token)

        # make ClientDetails object
        return ClientDetails(client_info)

    @classmethod
    def generate_keypair(self):
        public_key, private_key = Crypto.generate_keypair()
        return Crypto.encode_public_key(public_key), Crypto.encode_private_key(private_key)

    def client_info(self, client_id):
        url = self.__get_url("v1", "storage", "clients", client_id)
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        json = response.json()

        if response.status_code == 404:
            raise LookupError('Client ID not found: {0}'.format(client_id))

        client_id = json['client_id']
        public_key = json['public_key']
        validated = json['validated']
        return ClientInfo(client_id, public_key, validated)

    def __client_key(self, client_id):
        if client_id == self.client_id:
            return Crypto.decode_public_key(self.public_key)
        else:
            client_info = self.client_info(client_id).to_json()
            return Crypto.decode_public_key(client_info['public_key']['curve25519'])

    def __read_raw(self, record_id):
        url = self.__get_url("v1", "storage", "records", record_id)
        response = requests.get(url=url, auth=self.e3db_auth)
        self.__response_check(response)
        json = response.json()
        # craft meta object
        # craft record object
        meta_json = json['meta']
        data_json = json['data']
        meta = Meta(meta_json)
        record = Record(meta, data_json)
        return record

    def read(self, record_id):
        return self.__decrypt_record(self.__read_raw(record_id))

    def write(self, record_type, data, plain=None):
        url = self.__get_url("v1", "storage", "records")
        meta_data = {
            'writer_id': self.client_id,
            'user_id': self.client_id,
            'type': record_type,
            'plain': plain
        }
        meta = Meta(meta_data)
        record = Record(meta, data)
        encrypted_record = self.__encrypt_record(record)
        response = requests.post(url=url, json=encrypted_record.to_json(), auth=self.e3db_auth)
        self.__response_check(response)
        response_json = response.json()
        meta.update(response_json['meta']) # should be same
        decrypted = self.__decrypt_record(Record(meta, response_json['data']))
        return decrypted

    def update(self, record):
        record_serialized = record.to_json()
        record_id = record_serialized['meta']['record_id']
        version = record_serialized['meta']['version']
        url = self.__get_url("v1", "storage", "records", "safe", record_id, version)
        encrypted_record = self.__encrypt_record(record)
        response = requests.put(url=url, json=encrypted_record.to_json(), auth=self.e3db_auth)
        self.__response_check(response)
        json = response.json()
        new_meta = json['meta']
        record.get_meta().update(new_meta)

    def delete(self, record_id, version):
        url = self.__get_url("v1", "storage", "records", "safe", record_id, version)
        response = requests.delete(url=url, auth=self.e3db_auth)
        self.__response_check(response)

    def backup(self, client_id, registration_token):
        # credentials must be json encoded in order to decode
        # properly in the innovault console.
        credentials = {
            'version': '1',
            'client_id': "\"{0}\"".format(self.client_id),
            'api_key_id': "\"{0}\"".format(self.api_key_id),
            'api_secret': "\"{0}\"".format(self.api_secret),
            'client_email': "\"{0}\"".format(self.client_email),
            'public_key': "\"{0}\"".format(self.public_key),
            'private_key': "\"{0}\"".format(self.private_key),
            'api_url': "\"{0}\"".format(self.api_url)
        }

        self.write('tozny.key_backup', credentials, {'client': self.client_id})
        # share this record type with the backup client
        self.share('tozny.key_backup', client_id)

        url = self.__get_url('v1', 'account', 'backup', registration_token, self.client_id)
        response = requests.post(url=url, auth=self.e3db_auth)
        self.__response_check(response)

    def query(self, data=True, writer=[], record=[], record_type=[], plain=None, page_size=DEFAULT_QUERY_COUNT, last_index=0):
        all_writers = False
        if writer == "all":
            all_writers = True
            writer = []

        q = Query(after_index=last_index, include_data=data, writer_ids=writer, \
                record_ids=record, content_types=record_type, plain=plain, \
                user_ids=None, count=page_size, \
                include_all_writers=all_writers)

        response = self.__query(q)

        if 'error' in response:
            # we had an error, return this to user
            raise QueryError(response['error'])

        # take this apart
        last_index = response['last_index']
        results = response['results']
        records = []

        for result in results:
            result_meta = result['meta']
            meta = Meta(result_meta)
            result_data = result['record_data']
            record = Record(meta=meta, data=result_data)

            if data:
                # need to decrypt all the results before returning.
                access_key = result['access_key']
                if access_key:
                    ak = self.__decrypt_eak(access_key)
                    record = self.__decrypt_record_with_key(record, ak)
                else:
                    record = __decrypt_record(record)

            records.append(record)

        return QueryResult(q, records)

    # Fetch a single page of query results. Used internally by Client.query.
    def __query(self, query):
      url = self.__get_url('v1', 'storage', 'search')
      response = requests.post(url=url, json=query.to_json(), auth=self.e3db_auth)
      self.__response_check(response)
      return response.json()

    def share(self, record_type, reader_id):
        if reader_id == self.client_id:
            return

        ak = self.__get_access_key(self.client_id, self.client_id, self.client_id, record_type)
        self.__put_access_key(self.client_id, self.client_id, reader_id, record_type, ak)

        url = self.__get_url("v1", "storage", "policy", self.client_id, self.client_id, reader_id, record_type)

        json = {
            'allow': [
                {'read': {}}
            ]
        }

        response = requests.put(url=url, json=json, auth=self.e3db_auth)
        self.__response_check(response)

    def revoke(self, record_type, reader_id):
        if reader_id == self.client_id:
            return

        url = self.__get_url("v1", "storage", "policy", self.client_id, self.client_id, reader_id, record_type)
        json = {
            'deny': [
                {
                    'read': {}
                }
            ]
        }
        response = requests.put(url=url, json=json, auth=self.e3db_auth)
        self.__response_check(response)
        self.__delete_access_key(self.client_id, self.client_id, reader_id, record_type)
