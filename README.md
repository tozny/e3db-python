# Introduction

The Tozny End-to-End Encrypted Database (E3DB) is a storage platform with powerful sharing and consent management features.
[Read more on our blog.](https://tozny.com/blog/announcing-project-e3db-the-end-to-end-encrypted-database/)

E3DB provides a familiar JSON-based NoSQL-style API for reading, writing, and querying data stored securely in the cloud.

# Requirements

* Python 3.4+ environment (Version 1.x of the E3DB SDK supports 2.7, but is no longer being supported except in the case of security updates)

# Installation

## With Pip (Preferred)

`pip install e3db`

## Local build

### Build

To build the package locally:

```bash
python setup.py bdist_wheel
```

### Install

That produces a `.whl` file in the `dist` directory that you can install. This can be installed with:

```bash
pip install --use-wheel --find-links=<path to dist dir> e3db
```

# Setup

## Registering a client

Register an account with [InnoVault](https://innovault.io) to get started. From the Admin Console you can create clients directly (and grab their credentials from the console) or create registration tokens to dynamically create clients with `e3db.Client.register()`. Clients registered from within the console will automatically back their credentials up to your account. Clients created dynamically via the SDK can _optionally_ back their credentials up to your account.

For a more complete walkthrough, see [`/examples/registration.py`](https://github.com/tozny/e3db-python/blob/master/examples/registration.py).

### Without Credential Backup

```python
import e3db

token = '...'
client_name = '...'

public_key, private_key = e3db.Client.generate_keypair()

client_info = e3db.Client.register(token, client_name, public_key)

# Now run operations with the client's details in client_info
```

The object returned from the server contains the client's UUID, API key, and API secret (as well as echos back the public key passed during registration). It's your responsibility to store this information locally as it _will not be recoverable_ without credential backup.

### With Credential Backup

```python
import e3db

token = '...'
client_name = '...'

public_key, private_key = e3db.Client.generate_keypair()

client_info = e3db.Client.register(token, client_name, public_key, private_key=private_key, backup=True)

# Now run operations with the client's details in client_info
```

The private key must be passed to the registration handler when backing up credentials as it is used to cryptographically sign the encrypted backup file stored on the server. The private key never leaves the system, and the stored credentials will only be accessible to the newly-registered client itself or the account with which it is registered.

## Loading configuration and creating a client

Configuration is managed at runtime by instantiating an `e3db.Config` object with your client's credentials.

```python
import e3db
import os

# Assuming your credentials are stored as defined constants in the
# application, pass them each into the configuration constructor as
# follows:

config = e3db.Config(
    os.environ["client_id"],
    os.environ["api_key_id"],
    os.environ["api_secret"],
    os.environ["public_key"],
    os.environ["private_key"]
)

# Pass the configuration when building a new client instance.

client = e3db.Client(config())
```

# Usage

## Writing a record

To write new records to the database, call the `e3db.Client.write` method with a string describing the type of data to be written, along with an dictionary containing the fields of the record. `e3db.Client.write` returns the newly created record.

```python
import e3db

client = e3db.Client(
  # config
)

record_type = 'contact'
data = {
    'first_name': 'Jon',
    'last_name': 'Snow',
    'phone': '555-555-1212'
}

record = client.write(record_type, data)

print 'Wrote record {0}'.format(record.meta.record_id)
```

## Searching records

E3DB supports complex search options for finding records based on the fields stored in record metadata. 

For example, to list all records of type `contact` and print a simple report containing names and phone numbers:

```python
# setup
import e3db
from e3db import Search

config = e3db.Config(
    os.environ["client_id"],
    os.environ["api_key_id"],
    os.environ["api_secret"],
    os.environ["public_key"],
    os.environ["private_key"]
)

client = e3db.Client(config())

query = Search(include_data=True).Match(record_type=['contact'])
results = client.Search(query)

for record in results:
    full_name = "{0} --- {1}".format(record.data['first_name'], record.data['last_name'])
    print "{0} --- {1}".format(full_name, record.data['phone'])
```

The full list of parameters you can search for are under `e3db.types.Params`. Searching gives you access to chaining more powerful queries such as conditional operators, exclusions, and date filters.     

To search for records of type `season` that have unencrypted metadata values of `summer` and `sunny`, create the following query:
```python 
# e3db setup...

data = {"temp": "secret_temp"}
plain = {"name":"summer", "weather":"sunny"}
client.write("season", data, plain)

# {key:values} in the plain JSON field are mapped to keys=[] and values=[] behind the scenes in E3DB.
query = Search().Match(condition="AND", record_type=["season"], values=["summer", "sunny"])
results = client.Search(query)

# searching on keys instead...
query = Search().Match(condition="AND", record_type=["season"], keys=["name", "weather"])
```

To search for records of type `jam` with values of `apricot`, but excluding values of `strawberry`, create the following query:
```python 
# e3db setup...

apricot_data = {"recipe": "encrypted_secret_formula"}
apricot_plain = {"flavor":"apricot"}

client.write("jam", apricot_data, apricot_plain)

strawberry_data = {"recipe": "encrypted_secret_formula"}
strawberry_plain = {"flavor":"strawberry"}
client.write("jam", strawberry_data, strawberry_plain )

query = Search().Match(record_type=["jam"], values=["apricot"]).Exclude(values=["strawberry"])
results = client.Search(query)
```

To filter queries provide a datetime range and a valid timezone, to override the `UTC` default. Run the following search to get all records written by a specific user during the last 24 hours:
```python
# e3db setup...
from datetime import datetime, timedelta

# time T between start <-T-> end
end = datetime.now()
start =  end - timedelta(days=1)
writer_id = "some_writer_uuid"

query = Search().Match(writer=[writer_id]).Range(zone_offset="-08:00", start=start, end=end)
results = client.Search(query)
```

#### Defaults

The Search method has a number of default parameters when searching, more detail can be found within the inline documentation.

Under Search there are these defaults:
```python
# Optional value that starts search from the first page of results, only required for paginated queries.
next_token = 0

# Amount of records to be returned, limiting if more are available. Defaults to 50, and the maximum value allowed is 1000.
count = 50

# Include only records written by the client (False), or search other writer ids (True)
include_all_writers = False

# Include data when returning records
include_data = False
```

Under Search Params there are these defaults:
```python
# Conditional OR when searching upon all fields within this Param object
condition = "OR" # options: "OR"|"AND"

# Exactly matches the search fields provided
strategy = "EXACT" # options "EXACT"|"FUZZY"|"WILDCARD"|"REGEXP"
```

Under Search Range there is this default:
```python
# Search records based on when they were created or last modified
key = "CREATED" # options: "CREATED"|"MODIFIED"

# Default time provided is set to UTC.
zone = "UTC" # options are "PST":"-08:00", "MST":"-07:00", "CST":"-06:00", "EST":"-05:00", "UTC":"+00:00"

# Zone offset is None by default, but if provided it will override the default zone parameter
zone_offset = None
```

Since python datetime objects are zone agnostic, provide the proper timezone offset from UTC
in zone_offset to search properly.

### Advanced Matching Strategies

Search offers advanced queries that provide more flexibility than the default matching strategy of `EXACT`. The four options are `EXACT`, `FUZZY`, `WILDCARD`, and `REGEXP`. Depending on the matching strategy and the fields provided, these searches may be slower. 

To mirror some of the above queries with these matching strategies we get:
```python
# e3db setup...

# fuzzy
# generates an edit distance and matches fields that are 1-2 edits away from the provided query.
# summer is 1 edit s-> b away from bummer
fuzz_query = Search().Match(strategy="FUZZY", record_type=["season"], values=["bummer"])

# wildcard
# supported wildcards are * and ?
# * matches any character sequence, including the empty sequence.
# ? matches any single character
wild_query = Search().Match(strategy="WILDCARD", record_type=["season"], values=["su??er"])

# regexp
# some of the support operators are ^ $ . ? + * | { } [ ] ( ) \
# refer to the table below for more information
regxp_query = Search().Match(strategy="REGEXP", record_type=["season"], values=["sum.*"])
```

#### Regexp operators
```
^ anchors expression to the start of the matched strings
$ anchors expression to the end of the matched strings
. represents any single character
? used to match the preceding shortest pattern zero or one times
+ used to match the preceding shortest pattern one or more times
* used to match the preceding shortest pattern zero or more times
| acts as an OR operator, matches this OR that
{ } used to specify the min and max nubmer of times the preceding pattern can repeat. 
    - {2} repeat twice, {2,} repeat at least twice, {2,3} repeat 2-3 times
( ) used to group sub patterns
    - (ab)+ repeat the value within parenthesis 'ab' one or more times
[ ] used to specify a range of characters
    - [abc] matches 'a' or 'b' or 'c'
    - within the square brackets a ^ negates the class: [^abc] excludes characters 'a', 'b', and 'c'
\ is used to escape any of the previous special characters
```
For more information look [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-regexp-query.html)

### Paging

The construction of the Search object offers a number of options for paging through your results: namely `next_token` and `count`.

To page through a large number of results, you can loop like this:
```python
# e3db setup...
# limit number of results returned to 1000 at a time
query = Search(count=1000).Match(record_type=["many_results"])
results = client.Search(query)

# Number of results in e3db
total_results = results.total_results
# Return records from this point onwards in next query

while results.next_token:
    query.next_token = results.next_token
    results = client.Search(query)
    do_something(results) # process results
```

The `next_token` returned from a query will be 0 if there are no more records to return. `total_results` represents the total number of records in e3db that match the executed query. 

See [the integration tests](e3db/tests/test_search_integration.py) for more examples.

### Large Files

When searching or querying for large files, even if you set `include_data=True`, the data field returned will be blank. Instead file meta will be returned under each record's meta `record.meta.file_meta`. To download the file you can use the `e3db.Client.read_file` method like this:

```python
# e3db setup...

# record_id retrieved from search...
query = Search().Match(record_type=["large_file"])
results = client.Search(query)

# download large files
for i, r in enumerate(results):
    record_id = r.meta.record_id
    dest = "./large_file_{0}.txt".format(i)
    FileMeta = client.read_file(record_id, dest)
```

## Querying records

E3DB supports many options for querying records based on the fields stored in record metadata. Refer to the API documentation for the complete set of options that can be passed to `e3db.Client.query`.

For example, to list all records of type `contact` and print a simple report containing names and phone numbers:

```python
import e3db

client = e3db.Client(' config ')

record_type = 'contact'

for record in client.query(record=[record_type]):
    full_name = "{0} --- {1}".format(record.data['first_name'], record.data['last_name'])
    print "{0} --- {1}".format(full_name, record.data['phone'])
```

In this example, the `e3db.Client.query` method returns an iterator that contains each record that matches the query.

## More examples

See [the simple example code](https://github.com/tozny/e3db-python/blob/master/examples/simple.py) for runnable detailed examples.

## Cipher Suite Selection

The Python SDK is capable of operating in two different modes - Sodium and NIST. The Sodium mode uses [Libsodium](https://download.libsodium.org/doc/) for all cryptographic primitives. The NIST mode uses NIST-approved primitives via OpenSSL for all cryptographic primitives.

The SDK will operate in Sodium mode by default. To switch operation to NIST mode, export an environment variable before running any reliant applications:

```sh
export CRYPTO_SUITE=NIST
```

The NIST mode of operations will leverage:
- ECDH over curve P-384 for public/private key exchange
- SHA384 for hashing
- ECDSA over curve P-384 for cryptographic signatures
- AES265GCM for symmetric encryption operations

## Documentation

General E3DB documentation is [on our web site](https://tozny.com/documentation/e3db/).

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/tozny/e3db-python.

## License

Tozny dual licenses this product. For commercial use, please contact [info@tozny.com](mailto:info@tozny.com). For non-commercial use, this license permits use of the software only by government agencies, schools, universities, non-profit organizations or individuals on projects that do not receive external funding other than government research grants and contracts. Any other use requires a commercial license. For the full license, please see [LICENSE.md](https://github.com/tozny/e3db-python/blob/master/LICENSE.md), in this source repository.
