import e3db
import os
import binascii
import pytest
import time
import e3db.types
import hashlib
import requests
from datetime import datetime
from datetime import timedelta
from ..auth import E3DBAuth
from ..types import ClientDetails

api_url = os.environ["DEFAULT_API_URL"]
token = os.environ["REGISTRATION_TOKEN"]

class TestSearchIntegration():
    @classmethod
    def register_client(self):
        client1_public_key, client1_private_key = e3db.Client.generate_keypair()
        client1_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
        test_client1 = e3db.Client.register(token, client1_name, client1_public_key, api_url=api_url)
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

    @classmethod
    def setup_class(self):
        self.register_client()
        self.record_type = "SDK_integration_tests"
        self.record1 = self.client1.write(self.record_type, 
                                            {'time': str(time.time())}, 
                                            {'hello':'toznians',
                                            'regexp':'toznywebsite',
                                            'fuzzy':'veryveryfuzzy'
                                            })

        self.record2 = self.client1.write(self.record_type, 
                                            {'time': str(time.time())} )
        time.sleep(1) # Time needed for indexer to process record

    def test_v2_search_write_and_query(self):
        record1_id = self.record1.meta.record_id
        print(record1_id)
        q = e3db.types.Search(include_data=True).match(record=[record1_id])
        results = self.client1.search(q)
        for r in results:
            print("record:")
            print(r.to_json())
        assert(len(results) == 1)

    def test_v2_search_returns_nothing(self):
        q = e3db.types.Search(include_data=True).match(values=["ladsfkjadsklfjgarbagefdjsklafjkdljsaf"])
        results = self.client1.search(q)
        for r in results:
            print("record:")
            print(r.to_json())
        assert(len(results) == 0)

    def test_v2_exclude_only_record(self):
        q = e3db.types.Search().match(record_type=[self.record_type]).exclude(record=[self.record1.meta.record_id])
        results = self.client1.search(q)
        assert(len(results)==1)

    def test_v2_search_fuzzy(self):
        q = e3db.types.Search(include_data=True).match(strategy="FUZZY",values=["veryveryfunny"])
        results = self.client1.search(q)
        assert(len(results)==1)

    def test_v2_invalid_range(self):
        record1_id = self.record1.meta.record_id
        q = e3db.types.Search(include_data=True).match(record=[record1_id]).range(before=datetime.now(), after=datetime.now())
        results = self.client1.search(q)
        assert(len(results)==0)

    def test_v2_valid_range(self):
        record1_id = self.record1.meta.record_id
        q = e3db.types.Search(include_data=True).match(record=[record1_id]).range(zone="PST", before=datetime.now()+timedelta(hours=1), after=datetime.now()+timedelta(hours=-1))
        results = self.client1.search(q)
        assert(len(results)==2)

    def test_v2_multi_match(self):
        record1_id = self.record1.meta.record_id
        record2_id = self.record2.meta.record_id
        q = e3db.types.Search().match(record=[record1_id]).match(record=[record2_id])
        results = self.client1.search(q)
        assert(len(results)==2)

    def test_v2_multi_and_match(self):
        record1_id = self.record1.meta.record_id
        record2_id = self.record2.meta.record_id
        q = e3db.types.Search().match(condition="AND", record=[record1_id, record2_id])
        results = self.client1.search(q)
        assert(len(results)==0)

    def test_v2_receive_data(self):
        record1_id = self.record1.meta.record_id
        q = e3db.types.Search(include_data=True).match(record=[record1_id])
        results = self.client1.search(q)
        assert(len(results)==1)
        for r in results:
            assert(r.data is not None)

        q = e3db.types.Search(include_data=False).match(record=[record1_id])
        results = self.client1.search(q)
        assert(len(results)==1)
        for r in results:
            assert(r.data is None)

    def test_v2_search_regexp(self):
        q = e3db.types.Search(include_data=True).match(strategy="REGEXP", values=['tozny.*'])
        results = self.client1.search(q)
        for r in results:
            print("record:")
            print(r.to_json())
        assert(len(results) == 1)


