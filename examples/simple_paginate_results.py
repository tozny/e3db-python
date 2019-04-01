import e3db
from e3db.types import Search
import os
import json

credentials_path = "credentials.json" # your e3db credentialss

if os.path.exists(credentials_path):
    print("found", credentials_path)
    client = e3db.Client(json.load(open(credentials_path)))

    query = Search(include_all_writers=True, next_token=0, count=1000)
    results = client.search(query)

    print(results.total_results) # Total results available for searching within TozStore. If this exceeds 10k narrow your search, as we do not return results past than 10k.

    while results.next_token != 0: # Loop until we've hit found all records
        results = client.search(query)
        query.next_token = results.next_token
        for r in results:
            print(r.to_json())
