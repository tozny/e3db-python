import e3db
from e3db.types import Search
import os
import json
import time

registration_token = ''
# fill in with your client profile if you already have data written
client_name = "search_bool"

def main():
    try:
        client = e3db.Client(e3db.Config.load(client_name))
    except:
        register_and_write_credentials()
        client = e3db.Client(e3db.Config.load(client_name))

    # comment me if using a custom client or data is already written
    write_data(client)

    # Get all written records
    # By default Search(), the empty search, will match anything
    results = client.search(Search())
    print_results("Getting all records", results)

    # The Search Method has two conditional options for constructing your queries: AND|OR
    # OR is used by default and does not have to be explicitly stated as below.
    server_1_or_server_2 = Search().match(condition="OR", strategy="WILDCARD", plain={"*server_1*":"*", "*server_2*":"*"})
    results = client.search(server_1_or_server_2)
    print_results("getting records with server_1 or server_2 in meta with the plain field", results)

    server_1_and_server_2 = Search().match(condition="AND", strategy="WILDCARD", plain={"*server_1*":"*", "*server_2*":"*"})
    results = client.search(server_1_and_server_2)
    print_results("getting records with server_1 and server_2 in meta with the plain field (returns nothing)", results)

    # without using the plain dictionary
    server_1_or_server_2 = Search().match(condition="OR", strategy="WILDCARD", keys=["*server_1*", "*server_2*"])
    results = client.search(server_1_or_server_2)
    print_results("getting records with server_1 or server_2 using they keys field", results)

    # search fields can be intermingled
    # AND is the logical operator and returns records that match all conditions within the match parameters.
    record_and_plain_search = Search().match(condition="AND", strategy="WILDCARD", record_types=["flora"], plain={"*test*":"*dand*"})
    results = client.search(record_and_plain_search)
    # The results we see here is all records of record_type `flora`, and key `*test*` and value `*dand*`
    # We get the single record with meta "{'flora_test_12345':'dandelion'}"
    print_results("get records by record type 'flora' AND plain containing '*test*':'*dand*' ", results)

    # Chained match clauses with match or exclude clauses with exclude are joined by the logical OR
    chain_match = Search().match(condition="AND", record_types=["flora"]).match(condition="AND", record_types=["fauna"])
    # the above search is equivalent to below.
    equivalent_to_chain_match = Search().match(condition="OR", record_types=["flora", "fauna"])

    # Chaining excludes example: It inheritely matches everything by default if no `match` parameter is provided, 
    # and then excludes fields in exclude.

    # results = MATCH _ AND (EXCLUDE `flora` OR EXCLUDE `fauna`)
    chain_exclude = Search().exclude(condition="AND", record_types=["flora"]).exclude(condition="AND", record_types=["fauna"])
    # the above search is equivalent to below.
    equivalent_to_chain_exclude = Search().exclude(condition="OR", record_types=["flora", "fauna"])

    # Chaining match and exclude together will remove the exclude fields. 
    # This means records that equal the match clause AND do not equal the exclude clause are returned.
    match_and_exclude = Search().match(record_types=["flora"]).exclude(strategy="WILDCARD", keys=["*test*"])
    results = client.search(match_and_exclude)
    print_results("get records of record type 'flora' and do not have keys `*test*`", results)

    # Nested chaining allows you to specify varying strategies for different terms within a clause. 
    differing_strategies = Search().match(strategy="EXACT", record_types=["flora"])\
                                    .match(strategy="WILDCARD", keys=["*12345"])\
                                    .exclude(strategy="REGEXP", keys=[".*test.*"])\
                                    .exclude(strategy="REGEXP", keys=[".*server_2.*"])
    # results = (MATCH `flora` OR MATCH `*12345`) AND (EXCLUDE `.*test.*` OR EXCLUDE `.*server_2.*`)
    results = client.search(differing_strategies)
    print_results("Different matching strategies: this search will return an EXACT match to record_type `flora` OR WILDCARD match to keys `*12345`, and a REGEXP exclude to keys `.*test.*` OR REGEXP exclude to keys `.*server_2.*`", results)

    # Keep in mind that this chaining means your previous search object gets altered each time. 
    original_search = Search().exclude(record_types=["fauna"])
    modified_search = original_search.exclude(record_types=["flora"])
    results = client.search(modified_search)
    print_results("modified_search and original_search will exclude both flora and fauna", results)


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

    test_data = {'weight':'10.2', 'seeds':'one'}
    test_meta = {'prod_12345':'dandelion'}
    client.write("flora", test_data, test_meta)

    test_data = {'weight':'200', 'legs':'4'}
    test_meta = {'fauna_test_12345':'cat'}
    client.write("fauna", test_data, test_meta)

    test_data = {'weight':'5', 'seeds':'one', 'location':'oregon'}
    test_meta = {'flora_prod_server_1_12345':'rose'}
    client.write("flora", test_data, test_meta)

    test_data = {'weight':'300', 'legs':'4'}
    test_meta = {'fauna_prod_server_2_12345':'dog', 'walks':'false'}
    client.write("fauna", test_data, test_meta)

    test_data = {'weight':'500', 'legs':'5'}
    test_meta = {'fauna_server_3_12345':'weird_dog', 'walks':'true'}
    client.write("fauna", test_data, test_meta)

    test_data = {'weight':'???', 'legs':'N/A'}
    test_meta = {'funa_server_3_12345':'oops spelling'}
    client.write("fluna", test_data, test_meta)

# For demonstration purposes only. This will delete all of your records and is a permanent action.
def delete_all_data(client):
    results = client.search(Search())
    for r in results:
        client.delete(r.meta.record_id, r.meta.version)

def print_results(message, results):
    print(message)
    print([i.meta.plain for i in results])
    print()

if __name__ == "__main__":
    main()
