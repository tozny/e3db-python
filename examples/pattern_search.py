import e3db
from e3db.types import Search
import os
import json
import time

registration_token = ''
# fill in with your client profile if you already have data written
client_name = "search_pattern"

def main():
    try:
        client = e3db.Client(e3db.Config.load(client_name))
    except:
        register_and_write_credentials()
        client = e3db.Client(e3db.Config.load(client_name))

    write_data(client)

    # Get all written records
    results = client.search(Search())
    print_results("Getting all records", results)

    # Construct Wildcard Search for all Flora
    wild_search = Search().match(strategy="WILDCARD", keys=["flora*"])
    results = client.search(wild_search)
    print_results("Getting all flora records", results)

    # Construct Regex Search for all Fauna
    regex_search = Search().match(strategy="REGEXP", keys=[".*fauna.*"])
    results = client.search(regex_search)
    print_results("Getting all fauna records", results)

    # Construct Regex Search for all `test` tagged meta
    regex_test_search = Search().match(strategy="REGEXP", keys=[".*test.*"])
    results = client.search(regex_test_search)
    print_results("Getting all test records", results)

    # Exclude all `test` tagged meta from results
    exclude_test_search = Search().exclude(strategy="WILDCARD", keys=["*test*"])
    results = client.search(exclude_test_search)
    print_results("Excluding all test records", results)

    # Fuzzy Queries look for close words
    fuzzy_search = Search().match(strategy="FUZZY", record_types=["fauna"])
    results = client.search(fuzzy_search)
    print_results("Getting all records with record type close to 'fauna', includes record_type 'fluna'", results)

    # Get Flora meta records, but exclude test records with multiple strategies
    multiple_strategy_search = Search().match(strategy="WILDCARD", plain={"*flora*":"*"})\
                                        .exclude(strategy="REGEXP", keys=[".*test.*"])
    results = client.search(multiple_strategy_search )
    print_results("Gets records with 'flora' in the plain key with wildcards, but excludes all records with 'test' in the plain key", results)

# Create client and save client details
def register_and_write_credentials():
    public_key, private_key = e3db.Client.generate_keypair()
    client_info = e3db.Client.register(registration_token, client_name, public_key)
    config = e3db.Config(
        client_info.client_id,
        client_info.api_key_id,
        client_info.api_secret,
        public_key,
        private_key
    )
    config.write(client_name)

def write_data(client):
    # Write your data
    test_data = {'weight':'10.2', 'seeds':'many'}
    test_meta = {'flora_test_12345':'dandelion'}
    client.write("flora", test_data, test_meta)

    test_data = {'weight':'200', 'legs':'4'}
    test_meta = {'fauna_test_12345':'cat'}
    client.write("fauna", test_data, test_meta)

    test_data = {'weight':'5', 'seeds':'one', 'location':'oregon'}
    test_meta = {'flora_prod_server_1_12345':'rose'}
    client.write("flora", test_data, test_meta)

    test_data = {'weight':'300', 'legs':'4'}
    test_meta = {'fauna_prod_server_2_12345':'dog'}
    client.write("fauna", test_data, test_meta)

    test_data = {'weight':'500', 'legs':'5'}
    test_meta = {'fauna_server_3_12345':'weird_dog'}
    client.write("fauna", test_data, test_meta)

    test_data = {'weight':'???', 'legs':'N/A'}
    test_meta = {'funa_server_3_12345':'oops spelling'}
    client.write("fluna", test_data, test_meta)

# For demonstration purposes only. This will delete all of your records and is a permanent action.
def delete_data(client):
    results = client.search(Search())
    for r in results:
        client.delete(r.meta.record_id, r.meta.version)

def print_results(message, results):
    print(message)
    print([i.meta.plain for i in results])
    print()
                        
if __name__ == "__main__":
    main()
