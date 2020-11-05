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

Register an account with [Tozny](https://dashboard.tozny.com/login) to get started. From the Dashboard you can create clients directly (and grab their credentials from the console) or create registration tokens to dynamically create clients with `e3db.Client.register()`. Clients registered from within the console will automatically back their credentials up to your account. Clients created dynamically via the SDK can _optionally_ back their credentials up to your account.

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

api_key_id = client_info.api_key_id
api_secret = client_info.api_secret
client_id = client_info.client_id

config = e3db.Config(
    client_id,
    api_key_id,
    api_secret,
    public_key,
    private_key
)

# Optionally, if you want to save this Configuration to disk, do the following:
config.write()

# Now run operations with the client's details by instantiating a e3db client.
client = e3db.Client(config())
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

### Options for Loading Credentials
There are a number of options for instantiating an `e3db.Config` object. Shown above is the manual creation of the config option, but there are some convenience methods that can make this process easier when dealing with multiple client profiles.

Loading from `.tozny` profiles, takes advantage of the same profiles from the [e3db cli tool](https://github.com/tozny/e3db).
```python
# usage
config = e3db.Config.load(profile_name)
# path searched
path = `~/.tozny/<profile_name>/e3db.json`

# default path for no profile_name
config = e3db.Config.load()
path = `~/.tozny/e3db.json`

# provided method to save credentials to disk
config.write(profile_name)
```

Loading from an arbitrary file that matches the credentials format, but may have a custom path.
```python
credentials_path = "credentials.json" # your e3db credentialss
if os.path.exists(credentials_path):
    client = e3db.Client(json.load(open(credentials_path)))
    ...
```

# Usage

## Writing a record

To write new records to the database, call the `e3db.Client.write` method with a string describing the type of data to be written, along with an dictionary containing the terms of the record. `e3db.Client.write` returns the newly created record.

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
print ('Wrote record ID {0}'.format(record.meta.record_id))

# Read that record back from the server and print the name
record2 = client.read(record.meta.record_id)
print ('Read name: {0}'.format(record2.data['first_name']))

```

## Searching records

E3DB supports complex search options for finding records based on the terms stored in record metadata.
These terms include the properties in the [Meta class](e3db/types/meta.py):
```
 - record_ids
 - writer_ids
 - user_ids
 - record_types
 - plain
    - keys
    - values
```

The values in the plain meta dictionary are expanded into keys and values for two additional query terms:

```
 - keys
 - values

WHERE

 plain = {"key1":"value1", "key2":"value2"}
 keys = ["key1", "key2"]
 values = ["value1", "value2"]
```

A time range can be provided to limit search results based off one of these terms:
```
 - created
 - last_modified
```

#### Search Results

The results of your search come back in a [SearchResult object](e3db/types/search_result.py):

```python
# This object contains your records,
# and additional information about your search.

query = Search(include_data=True)
results = client.search(query)

# Records found in your search
results.records

# Number of records returned from search
len(results)

# Number of records present in E3db that match your search.
# If there are more records to be retrieved this number will be greater than len(results),
# and next_token will not be 0
results.total_results

# Token for paginating through queries,
# this token will be 0 if there are no more records to be returned.
results.next_token

results.search_id # id for bulk searching of many records, currently not available
```

#### Examples

To list all records of type `contact` and print a simple report containing names and phone numbers:

```python
# setup
import e3db
from e3db.types import Search

config = e3db.Config(
    os.environ["client_id"],
    os.environ["api_key_id"],
    os.environ["api_secret"],
    os.environ["public_key"],
    os.environ["private_key"]
)

client = e3db.Client(config())

query = Search(include_data=True).match(record_types=['contact'])
results = client.search(query)

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
query = Search().match(condition="AND", record_types=["season"], values=["summer", "sunny"])
results = client.search(query)

# searching on keys instead...
query = Search().match(condition="AND", record_types=["season"], keys=["name", "weather"])
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

query = Search().match(record_types=["jam"], values=["apricot"]).exclude(values=["strawberry"])
results = client.search(query)
```

#### Time Filters

The Search method has the capability to filter by the time records were created or last modified, restricting search results to a specific timeframe. The most basic example, of searching for all records written by a writer in the last 24 hours, is shown below:

```python
# e3db setup...
from e3db.types import Search
from datetime import datetime, timedelta
import time

# Using seconds from unix epoch
now = int(time.time())
start = now - (60 * 60 * 24) # 60 seconds, 60 minutes, 24 hours
end = now

writer_id = "some_writer_uuid"
query = Search().match(writers=[writer_id])\
    .range(start=start, end=end) # Filters here
results = client.search(query)

# using datetime
now = datetime.now().astimezone()
start = now - timedelta(days=1)
end = now

writer_id = "some_writer_uuid"
query = Search().match(writers=[writer_id])\
    .range(start=start, end=end) # Filters here
results = client.search(query)
```

The Range can be open ended if you want to, for example, see all records written before yesterday:
```python
now = int(time.time())
end = now - (60 * 60 * 24) # 60 seconds, 60 minutes, 24 hours == 1 day in seconds

query = Search().match()\
    .range(end=end)
results = client.search(query)
```

Or see all records written in the last week...

```python
now = int(time.time())
start = now - (60 * 60 * 24 * 7) # 60 seconds, 60 minutes, 24 hours, 7 days == 1 week in seconds

query = Search().match()\
    .range(start=start)
results = client.search(query)
```

The Search Range accepts Unix Epoch, datetime objects, and datetime timezone-unaware objects, for start and end times. In Python all datetime objects are `timezone naive` or `timezone-unaware` unless you are using a libary like pytz. So the Search Range will assume that you want a timezone of UTC unless otherwise specified.

To target a specific timezone you have a couple options:
```python
# 1. Go zone agnostic by providing a time based off of the Unix Epoch (recommended).
unix_epoch = int(time.time()) # https://www.epochconverter.com/ for conversions
query = Search().match().range(start=unix_epoch-3600, end=unix_epoch) # This will always return the most recent hour of results

# 2. Create timezone aware objects to pass into Search Range.
tz_unaware = datetime.now()
tz_aware = tz_unaware.astimezone() # sets timezone to match local machine

# 3. Specify an approriate zone_offset. The hour offset from UTC as int or "[+|-]HH:MM" as str
tz_unaware = datetime.now()
query = Search().match().range(start=tz_unaware, zone_offset=-7) # we append UTC-7 to the tz_unaware object
query = Search().match().range(start=tz_unaware, zone_offset="-07:00") # we parse and append UTC-7 to the tz_unaware object

# 4. Manually creating the proper time (not recommended).
tz_unaware = datetime.now()
# Assuming local tz of Pacific time, PT is UTC-7, and so we add 7 hours to get UTC.
utc_tz_unaware = tz_unaware + timedelta(hours=7)
query = Search().match().range(start=utc_tz_unaware)
```

Take care when using the python datetime library function `astimezone()`, because it does an implicit conversion behind the scenes using the computer's local timezone if no tzinfo is provided as a parameter. To avoid this you can replace the tzinfo instead:
```python
unaware_day = datetime(year=2019, month=3, day=18, hour=0, minute=0, second=0)
print(unaware_day.isoformat("T"))
# Prints: 2019-03-18T00:00:00

# using astimezone()
as_timezone = unaware_day.astimezone(timezone(timedelta(hours=0))) # attempting to convert to UTC
print(as_timezone.isoformat("T"))
# Prints: 2019-03-18T07:00:00+00:00, which is 7 hours ahead of the anticipated time.

# replacing tzinfo
aware_day = unaware_day.replace(tzinfo=timezone(timedelta(hours=0))) # attempting to convert to UTC
print(aware_day.isoformat("T"))
# Prints: 2019-03-18T00:00:00-07:00
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
# Conditional OR when searching upon all terms within this clause (Param object)
condition = "OR" # options: "OR"|"AND"

# Exactly matches the search terms provided
strategy = "EXACT" # options "EXACT"|"FUZZY"|"WILDCARD"|"REGEXP"
```

Under Search Range there is this default:
```python
# Search records based on when they were created or last modified
key = "CREATED" # options: "CREATED"|"MODIFIED"

# Zone offset is None by default, but if provided it will override provided datetime objects if they are timezone unaware
# Accepts
#   - int denoting hours offset from UTC
#   - str in the format "[+|-]HH:MM" also denoting the time offset from UTC
#       - for a more comprehensive list see https://en.wikipedia.org/wiki/List_of_UTC_time_offsets
zone_offset = None
```
Since python datetime objects are zone agnostic, provide the proper timezone offset from UTC
in zone_offset to search properly.

### Boolean Searching

Within each match or exclude clause the internal search terms can either be joined with AND or OR.

The data for these examples can be found under [boolean_search](./examples/boolean_search.py)

```python
# The Search Method has two conditional options for constructing your queries: AND|OR
# OR is used by default and does not have to be explicitly stated unlike below.
server_1_or_server_2 = Search().match(condition="OR", strategy="WILDCARD", plain={"*server_1*":"*", "*server_2*":"*"})
results = client.search(server_1_or_server_2)
print_results("getting records with server_1 or server_2 in meta with the plain field", results)

server_1_and_server_2 = Search().match(condition="AND", strategy="WILDCARD", plain={"*server_1*":"*", "*server_2*":"*"})
results = client.search(server_1_and_server_2)
print_results("getting records with server_1 and server_2 in meta with the plain field (returns nothing)", results)
```

Search terms can be intermingled

```python
# AND is the logical operator and returns records that match all conditions within the match parameters.
record_and_plain_search = Search().match(condition="AND", strategy="WILDCARD", record_types=["flora"], plain={"*test*":"*dand*"})
results = client.search(record_and_plain_search)
# The results we see here is all records of record_type `flora`, and key `*test*` and value `*dand*`
# We get the single record with meta "{'flora_test_12345':'dandelion'}"
print_results("get records by record type 'flora' AND plain containing '*test*':'*dand*' ", results)
```

Combining match and exclude together will remove the terms in the exclude clause
```python
# This means records that equal the match clause AND do not equal the exclude clause are returned.
match_and_exclude = Search().match(record_types=["flora"]).exclude(strategy="WILDCARD", keys=["*test*"])
results = client.search(match_and_exclude)
print_results("get records of record type 'flora' and do not have keys `*test*`", results)
```

Chaining match clauses with matches, and exclude clauses with excludes are joined by the logical OR. In general, the two basic tenants of chaining these clauses are as follows:
1. more match clauses expands your search, adding terms that match your results
1. more exclude clauses constricts your search, removing terms that match your results
```python
chain_match = Search().match(condition="AND", record_types=["flora"]).match(condition="AND", record_types=["fauna"])
# the above search is equivalent to below.
equivalent_to_chain_match = Search().match(condition="OR", record_types=["flora", "fauna"])
```

Nested chaining allows you to specify varying strategies for different terms
```python
differing_strategies = Search().match(strategy="EXACT", record_types=["flora"])\
                                .match(strategy="WILDCARD", keys=["*12345"])\
                                .exclude(strategy="REGEXP", keys=[".*test.*"])\
                                .exclude(strategy="REGEXP", keys=[".*server_2.*"])
# results = (MATCH `flora` OR MATCH `*12345`) AND (EXCLUDE `.*test.*` OR EXCLUDE `.*server_2.*`)
results = client.search(differing_strategies)
print_results("Different matching strategies: this search will return an EXACT match to record_type `flora` OR WILDCARD match to keys `*12345`, and a REGEXP exclude to keys `.*test.*` OR REGEXP exclude to keys `.*server_2.*`", results)
```

Keep in mind that this chaining means your previous search object gets altered each time.
```python
original_search = Search().exclude(record_types=["fauna"])
modified_search = original_search.exclude(record_types=["flora"])
results = client.search(modified_search)
print_results("modified_search and original_search will exclude both flora and fauna", results)
```

### Advanced Matching Strategies

Search offers advanced queries that provide more flexibility than the default matching strategy of `EXACT`. These are the four options ordered from fastest to slowest: `EXACT`, `FUZZY`, `WILDCARD`, and `REGEXP`.

To mirror some of the above queries with these matching strategies we get:
```python
# e3db setup...

# fuzzy
# generates an edit distance and matches terms that are 1-2 edits away from the provided query.
# summer is 1 edit s-> b away from bummer
fuzz_query = Search().match(strategy="FUZZY", record_types=["season"], values=["bummer"])

# wildcard
# supported wildcards are * and ?
# * matches any character sequence, including the empty sequence.
# ? matches any single character
wild_query = Search().match(strategy="WILDCARD", record_types=["season"], values=["su??er"])

# regexp
# some of the support operators are ^ $ . ? + * | { } [ ] ( ) \
# refer to the table below for more information
regxp_query = Search().match(strategy="REGEXP", record_types=["season"], values=["sum.*"])
```

Go to [Pattern Search Examples](./examples/pattern_search.py) for more examples.

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

See [the integration tests](e3db/tests/test_search_integration.py) or [examples folder](examples/) for more examples.

### Paging

The construction of the Search object offers a number of options for paging through your results: namely `next_token` and `count`.

To page through a large number of results, you can loop like this:
```python
# e3db setup...
# limit number of results returned to 1000 at a time
query = Search(count=1000).match(record_types=["many_results"])
results = client.search(query)

# Number of results in e3db
total_results = results.total_results
# Process the first set of results
if total_results > 0:
    do_something(results) # process results
# If there are more records to fetch, e.g. next_token != 0
# make subsequent searches using the next token to grab the next set of results
while results.next_token:
    query.next_token = results.next_token
    results = client.search(query)
    do_something(results) # process results
```

The `next_token` returned from a query will be 0 if there are no more records to return. `total_results` represents the total number of records in e3db that match the executed query.

See [pagination example](examples/simple_paginate_results.py) for full code example.

#### Search Count Restraints

You aren't limited to a specific number of searches, however for a single search the maximum page size is 1000. Requesting for a larger page size than 1000 (`count=1001`) will result in a HTTP 400 Bad Request. The pagination example, shown above, can be used to grab more than 1000 records overall.

```
query = Search(count=1000)
```

Additionally, if your search is too broad you will only be able to retrieve 10,000 results. You can choose to narrow your query by constricting time ranges manually or programatically as shown here with this [sample script](examples/narrow_range_of_large_search.py).

### Large Files

When searching or querying for large files, even if you set `include_data=True`, the data field returned will be blank. Instead file meta will be returned under each record's meta `record.meta.file_meta`. To download the file you can use the `e3db.Client.read_file` method like this:

```python
# e3db setup...

# record_id retrieved from search...
query = Search().match(record_types=["large_file"])
results = client.search(query)

# download large files
for i, r in enumerate(results):
    record_id = r.meta.record_id
    dest = "./large_file_{0}.txt".format(i)
    FileMeta = client.read_file(record_id, dest)
```

## Querying records

E3DB supports many options for querying records based on the terms stored in record metadata. Refer to the API documentation for the complete set of options that can be passed to `e3db.Client.query`.

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
- AES256GCM for symmetric encryption operations

## Documentation

General E3DB documentation is [on our web site](https://tozny.com/documentation/e3db/).

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/tozny/e3db-python.

## License

Tozny dual licenses this product. For commercial use, please contact [info@tozny.com](mailto:info@tozny.com). For non-commercial use, this license permits use of the software only by government agencies, schools, universities, non-profit organizations or individuals on projects that do not receive external funding other than government research grants and contracts. Any other use requires a commercial license. For the full license, please see [LICENSE.md](https://github.com/tozny/e3db-python/blob/master/LICENSE.md), in this source repository.
