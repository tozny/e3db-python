import e3db
import os
import binascii
import pytest
import time
import e3db.types

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

    def test_conflicting_updates(self):
        '''
        Test to check that an exception is raised when doing conflicting
        updates on a record.
        '''
        starting_time = str(time.time())
        data = {
            'time': starting_time
        }

        record = self.client1.write('test_result', data)
        updated_time = str(time.time())

        record_data = record.get_data()
        record_meta = record.get_meta()
        record_data['time'] = updated_time

        record1 = e3db.types.Record(record_meta, record_data)
        record2 = e3db.types.Record(record_meta, record_data)

        assert(record1.to_json() == record2.to_json())
        self.client1.update(record1)

        with pytest.raises(e3db.APIError):
            self.client1.update(record2)


    def test_query_by_type(self):
        '''
        Test we can get query results when looking for a specific record type,
        only including that record type.
        '''
        record_type = "test_type_{0}".format(binascii.hexlify(os.urandom(16)))
        starting_time = str(time.time())
        data = {
            'time': starting_time
        }
        record1 = self.client1.write(record_type, data)

        results = self.client1.query(record_type=[record_type])
        assert(len(results) >= 1)

        for record in results:
            assert(record.to_json()['data'] == data)

    def test_query_and_delete(self):
        '''
        Test to query records by record id, and delete them.
        '''
        record_type = "test_type_{0}".format(binascii.hexlify(os.urandom(16)))
        record1 = self.client1.write(record_type, {'time': str(time.time())})
        record1_id = record1.to_json()['meta']['record_id']
        record1_version = record1.to_json()['meta']['version']

        record2 = self.client1.write(record_type, {'time': str(time.time())})
        record2_id = record2.to_json()['meta']['record_id']
        record2_version = record2.to_json()['meta']['version']

        results = self.client1.query(record=[record1_id, record2_id], data=False)
        assert(len(results) == 2)

        for record in results:
            assert(record.to_json()['meta']['type'] == record_type)

        self.client1.delete(record1_id, record1_version)
        self.client1.delete(record2_id, record2_version)

        after_delete_results = self.client1.query(record=[record1_id, record2_id], data=False)

        assert(len(after_delete_results) == 0)

    def test_query_writer_id(self):
        '''
        Test to query records by writer id.
        '''
        writer_id = self.test_client1.get_client_id()
        for record in self.client1.query(writer=[writer_id], data=False):
            assert(record.to_json()['meta']['writer_id'] == writer_id)

    def test_query_plain(self):
        '''
        Test we can do a basic query by matching plaintext meta.
        '''
        plain_id = "id_{0}".format(binascii.hexlify(os.urandom(16)))

        plain_data = {
            'id': plain_id
        }

        starting_time = str(time.time())
        data = {
            'time': starting_time
        }
        record1 = self.client1.write('test-plain', data, plain=plain_data)

        query = {
                'eq': {
                    'name': 'id',
                    'value': plain_id
                }
            }

        results = self.client1.query(plain=query)
        assert(len(results) >= 1)

        for record in results:
            assert(record.to_json()['meta']['record_id'] == record1.to_json()['meta']['record_id'])

    # basic plaintext query
    # complex plaintext query