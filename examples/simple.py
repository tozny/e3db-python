# This program provides a few simple examples of reading, writing, and
# querying e3db records. For more detailed information, please see the
# documentation home page: https://tozny.com/documentation/e3db/
#
# Copyright: Copyright (c) 2017 Tozny, LLC


def generate_unlock_code():
    # Example function to give us back a 5 digit "combination lock" code,
    # padded with zeros as needed, just for our tools example.
    # generate a secure random number for our tools combination lock.
    import random
    csprng = random.SystemRandom()
    # 5 digit combo
    random_combo = csprng.randint(0, 99999)
    return '{:05d}'.format(random_combo)


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------
import e3db

# Configuration files live in ~/.tozny and you can have several
# different "profiles" like *dev* and *production*.

# Load ~/.tozny/dev/e3db.json profile
# conf = e3db.Config.load('dev')

# Load default config in ~/.tozny/e3db.json
conf = e3db.Config.load()

# Now create a client using that configuration.
client = e3db.Client(conf)

# ---------------------------------------------------------
# Writing a record
# ---------------------------------------------------------

record_type = 'Tool'

# Create a record by first creating a local version as a dictionary:
data = {
    'Storage': 'Blue Locked Tool Chest',
    'Unlock Code': generate_unlock_code()
}

# Now encrypt the *value* part of the record, write it to the server and
# the server returns the newly created record:

record = client.write(record_type, data)
record_id = record.meta.record_id
record_version = record.meta.version
print("Wrote: {0}".format(record_id))

# ---------------------------------------------------------
# Simple reading and queries
# ---------------------------------------------------------

# Use the new record's unique ID to read the same record again from E3DB:
new_record = client.read(record_id)
print("Record: {0} {1}".format(new_record.data['Storage'], new_record.data['Unlock Code']))

# Query for all records of type 'test-contact' and print out
# a little bit of data and metadata.

for record in client.query(record_type=[record_type]):
    print("Data: {0} {1}".format(record.data['Storage'], record.data['Unlock Code']))
    print("Metadata: {0} {1}".format(str(record.meta.record_id), record.meta.record_type))

# ---------------------------------------------------------
# Simple sharing by record type
# ---------------------------------------------------------

# Share all of the records of type 'Tool' with Isaac's client ID:
isaac_client_id = 'db1744b9-3fb6-4458-a291-0bc677dba08b'
client.share(record_type, isaac_client_id)

# ---------------------------------------------------------
# More complex queries
# ---------------------------------------------------------

# Create some new records of the same type (note that they are also shared
# automatically since they are a type that we have shared above. We
# will also add some "plain" fields that are not secret but can be used
# for efficient querying:

shovel_plain = {
    "Location": "Shed",
    "Tool": "Shovel"
}
shovel_data = {
    "Storage": "Green Locked Tool Chest",
    "Unlock Code": generate_unlock_code()
}
client.write(record_type, shovel_data, shovel_plain)

hammer_plain = {
    "Location": "Shed",
    "Tool": "Hammer"
}
hammer_data = {
    "Storage": "Red Locked Tool Chest",
    "Unlock Code": generate_unlock_code()
}
client.write(record_type, hammer_data, hammer_plain)

drill_plain = {
    "Location": "Garage",
    "Tool": "Drill"
}
drill_data = {
    "Storage": "Black Locked Storage Box",
    "Unlock Code": generate_unlock_code()
}
client.write(record_type, drill_data, drill_plain)

# Create a query that finds all tool storage locations that are Hammers, but not others:
hammer_query = {
    'eq': {
        'name': 'Tool',
        'value': 'Hammer'
    }
}

# Execute that query:
for record in client.query(plain=hammer_query):
    print("Data: {0} {1}".format(record.data['Storage'], record.data['Unlock Code']))

# Now create a more complex query with only the Hammers that are in the Shed
drill_query = {
    'and': [
        {
            'eq': {
                'name': 'Location',
                'value': 'Shed'
            },
        },
        {
            'eq': {
                'name': 'Tool',
                'value': 'Hammer'
            },
        },
    ]
}

# Execute that query:
for record in client.query(plain=drill_query):
    print("Data: {0} {1}".format(record.data['Storage'], record.data['Unlock Code']))

# ---------------------------------------------------------
# Learning about other clients
# ---------------------------------------------------------

isaac_client_info = client.client_info(isaac_client_id)

# Get the public key:
print("Isaac Public Key: {0}".format(isaac_client_info.public_key))

# ---------------------------------------------------------
# Clean up - Comment these out if you want to experiment
# ---------------------------------------------------------

# Revoke the sharing created by the client.share
client.revoke(record_type, isaac_client_id)

# Delete the record we created above
client.delete(record_id, record_version)

# Delete all of the records of type Tool from previous runs:
for record in client.query(record_type=[record_type]):
    client.delete(record.meta.record_id, record.meta.version)
