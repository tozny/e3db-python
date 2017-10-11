import e3db
import os
import binascii

token = os.environ["REGISTRATION_TOKEN"]
api_url = os.environ["DEFAULT_API_URL"]

class TestClient():
    @classmethod
    def setup_class(self):
        client1_public_key, client1_private_key = e3db.Client.generate_keypair()
        client1_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client1 = e3db.Client.register(token, client1_name, client1_public_key, api_url=api_url)
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
