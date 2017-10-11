import e3db
import os
import binascii
import pytest
import time

token = os.environ["REGISTRATION_TOKEN"]
api_url = os.environ["DEFAULT_API_URL"]

class TestClient():
    @classmethod
    def setup_class(self):
        '''
        Setup where we create two clients using registration tokens to associate
        them with out Innovault account. They will be used to test operations
        later in the integration tests where we don't want to create a new client
        every time.
        '''
        client1_public_key, client1_private_key = e3db.Client.generate_keypair()
        client1_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client1 = e3db.Client.register(token, client1_name, client1_public_key, api_url=api_url)
        self.test_client1 = test_client1
        client1_api_key_id, client1_api_secret = test_client1.get_api_credentials()
        client1_id = test_client1.get_client_id()

        client1_config = e3db.Config(
            client1_id, \
            client1_api_key_id, \
            client1_api_secret, \
            client1_public_key, \
            client1_private_key, \
            api_url=api_url \
            )

        self.client1 = e3db.Client(client1_config())

        client2_public_key, client2_private_key = e3db.Client.generate_keypair()
        client2_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client2 = e3db.Client.register(token, client2_name, client2_public_key, api_url=api_url)
        self.test_client2 = test_client2
        client2_api_key_id, client2_api_secret = test_client2.get_api_credentials()
        client2_id = test_client2.get_client_id()

        client2_config = e3db.Config(
            client2_id, \
            client2_api_key_id, \
            client2_api_secret, \
            client2_public_key, \
            client2_private_key, \
            api_url=api_url \
            )

        self.client2 = e3db.Client(client2_config())

    def test_can_register_client(self):
        '''
        Create and register a client using registration token to associate it
        with our Innovault account.
        '''
        public_key, private_key = e3db.Client.generate_keypair()
        client_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client = e3db.Client.register(token, client_name, public_key, api_url=api_url)

        api_key_id, api_secret = test_client.get_api_credentials()
        test_client_public_key = test_client.get_public_key()
        test_name = test_client.get_name()
        client_id = test_client.get_client_id()

        assert(api_key_id != "")
        assert(api_secret != "")
        assert(client_id != "")
        assert(public_key == test_client_public_key)
        assert(client_name == test_name)

    def test_can_register_client_backup(self):
        '''
        Create and register a client using registration token to associate it
        with our Innovault account. Also backup the client credentials to
        the backup client for later key recovery.
        '''
        public_key, private_key = e3db.Client.generate_keypair()
        client_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client = e3db.Client.register(token, client_name, public_key, private_key=private_key, backup=True, api_url=api_url)

        api_key_id, api_secret = test_client.get_api_credentials()
        test_client_public_key = test_client.get_public_key()
        test_name = test_client.get_name()
        client_id = test_client.get_client_id()

        assert(api_key_id != "")
        assert(api_secret != "")
        assert(client_id != "")
        assert(public_key == test_client_public_key)
        assert(client_name == test_name)

    def test_get_client_info(self):
        '''
        Test we can ask the server for our client info, and client_id matches
        the same that we have locally.
        '''
        client1_id = self.test_client1.get_client_id()
        info = self.client1.client_info(client1_id)
        assert(info.to_json()['client_id'] == self.test_client1.get_client_id())

    def test_client_doesnt_exist(self):
        '''
        Test we raise an exception for client that doesn't exist.
        '''
        with pytest.raises(e3db.APIError):
            self.client1.client_info('doesnt exist')

    def test_write_then_read_record(self):
        '''
        Test client1 can write a record, then read it back.
        Making sure that the original data handed to write is untampered with
        in it's unencrypted form.
        '''
        test_time = str(time.time())
        data = {
            'time': test_time
        }
        record1 = self.client1.write('test_result', data)

        record_id = record1.to_json()['meta']['record_id']
        record2 = self.client1.read(record_id)

        assert(record1 != record2)
        assert(data['time'] == test_time)
        assert(record2.to_json()['data']['time'] == test_time)
        assert(record2.to_json()['data'] == data)

    def test_write_update_read_record(self):
        '''
        Test client1 can write a record, update it, then read it back.
        '''
        starting_time = str(time.time())
        data = {
            'time': starting_time
        }

        record1 = self.client1.write('test_result', data)
        old_version = record1.to_json()['meta']['version']
        record_id = record1.to_json()['meta']['record_id']

        updated_time = str(time.time())

        record_data = record1.get_data()
        record_meta = record1.get_meta()
        record_data['time'] = updated_time
        record1.update(record_meta, record_data)
        self.client1.update(record1)

        read_record1 = self.client1.read(record_id)
        new_version = read_record1.to_json()['meta']['version']
        assert(starting_time != updated_time)
        assert(old_version != new_version)
        assert(read_record1.to_json()['data']['time'] == updated_time)
