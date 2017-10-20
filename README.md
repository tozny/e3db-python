# Introduction

The Tozny End-to-End Encrypted Database (E3DB) is a storage platform with powerful sharing and consent management features.
[Read more on our blog.](https://tozny.com/blog/announcing-project-e3db-the-end-to-end-encrypted-database/)

E3DB provides a familiar JSON-based NoSQL-style API for reading, writing, and querying data stored securely in the cloud.

# Installation

## Build

To build the package:

```bash
python setup.py bdist_wheel
```

## Install

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
    os.environ["client_id"], \
    os.environ["api_key_id"], \
    os.environ["api_secret"], \
    os.environ["public_key"], \
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

## Querying records

E3DB supports many options for querying records based on the fields stored in record metadata. Refer to the API documentation for the complete set of options that can be passed to `e3db.Client.query`.

For example, to list all records of type `contact` and print a simple report containing names and phone numbers:

```python
import e3db

client = e3db.Client(' config ')

record_type = 'contact'

for record in client.query(record=[record_type]):
    full_name = record.data['first_name'] + ' ' + record.data['last_name']
    print "{0} --- {1}".format(full_name, record.data['phone'])
```

In this example, the `e3db.Client.query` method returns an iterator that contains each record that matches the query.

## More examples

See [the simple example code](https://github.com/tozny/e3db-python/blob/master/examples/simple.py) for runnable detailed examples.

## Documentation

General E3DB documentation is [on our web site](https://tozny.com/documentation/e3db/).

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/tozny/e3db-python.

## License

Tozny dual licenses this product. For commercial use, please contact [info@tozny.com](mailto:info@tozny.com). For non-commercial use, this license permits use of the software only by government agencies, schools, universities, non-profit organizations or individuals on projects that do not receive external funding other than government research grants and contracts. Any other use requires a commercial license. For the full license, please see [LICENSE.md](https://github.com/tozny/e3db-python/blob/master/LICENSE.md), in this source repository.
