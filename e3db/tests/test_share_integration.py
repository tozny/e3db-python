import e3db
import os
import binascii
import pytest
import time
import e3db.types
import hashlib

token = os.environ["REGISTRATION_TOKEN"]
api_url = os.environ["DEFAULT_API_URL"]


def crypto_mode():
    if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
        return 'nist'

    return 'sodium'


class TestShareIntegration():
    @classmethod
    def setup_class(self):
        """
        Setup where we create two clients using registration tokens to associate
        them with out Innovault account. They will be used to test operations
        later in the integration tests where we don't want to create a new client
        every time.
        """
        client1_public_key, client1_private_key = e3db.Client.generate_keypair()
        client1_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client1 = e3db.Client.register(token, client1_name, client1_public_key, api_url=api_url)
        self.test_client1 = test_client1
        client1_api_key_id = test_client1.api_key_id
        client1_api_secret = test_client1.api_secret
        client1_id = test_client1.client_id

        client1_config = e3db.Config(
            client1_id,
            client1_api_key_id,
            client1_api_secret,
            client1_public_key,
            client1_private_key,
            api_url=api_url
        )

        self.client1 = e3db.Client(client1_config())

        client2_public_key, client2_private_key = e3db.Client.generate_keypair()
        client2_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client2 = e3db.Client.register(token, client2_name, client2_public_key, api_url=api_url)
        self.test_client2 = test_client2
        client2_api_key_id = test_client2.api_key_id
        client2_api_secret = test_client2.api_secret
        client2_id = test_client2.client_id

        client2_config = e3db.Config(
            client2_id,
            client2_api_key_id,
            client2_api_secret,
            client2_public_key,
            client2_private_key,
            api_url=api_url
        )

        self.client2 = e3db.Client(client2_config())

        client3_public_key, client3_private_key = e3db.Client.generate_keypair()
        client3_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client3 = e3db.Client.register(token, client3_name, client3_public_key, api_url=api_url)
        self.test_client3 = test_client3
        client3_api_key_id = test_client3.api_key_id
        client3_api_secret = test_client3.api_secret
        client3_id = test_client3.client_id

        client3_config = e3db.Config(
            client3_id,
            client3_api_key_id,
            client3_api_secret,
            client3_public_key,
            client3_private_key,
            api_url=api_url
        )

        self.client3 = e3db.Client(client3_config())

    def test_share_no_record(self):
        record_type = "sharing"
        self.client1.share(record_type, self.client2.client_id)
        data = {"is caring": "yes"}
        record = self.client1.write(record_type, data)
        self.client2.read(record.meta.record_id) 
        
    def test_share_no_record_cache_clear_self_read(self):
        record_type = "sharing2"
        self.client1.share(record_type, self.client2.client_id)
        data = {"is caring": "yes"}
        record = self.client1.write(record_type, data)
        self.client2.read(record.meta.record_id) 
        self.client1.read(record.meta.record_id)

        self.client1.ak_cache = {}

        self.client1.read(record.meta.record_id)
    
    def test_share_twice(self):
        record_type = "sharing3"
        self.client1.share(record_type, self.client2.client_id)
        self.client1.revoke(record_type, self.client2.client_id)
        self.client1.share(record_type, self.client2.client_id)