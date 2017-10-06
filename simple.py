import e3db

# Example function to give us back a 5 digit "combination lock" code,
# padded with zeros as needed, just for our tools example.
def generate_unlock_code():
    # generate a secure random number for our tools combination lock.
    import os
    import random
    import sys
    csprng = random.SystemRandom()
    # 5 digit combo
    random_combo = csprng.randint(0, 99999)
    return '{:05d}'.format(random_combo)


conf = e3db.Config.load('dev-python')
client = e3db.Client(conf)

record_type = 'Tools'

# Shovel
shovel_plain = {
    "Location": "Shed",
    "Storage": "Green Locked Tool Chest",
    "Tool": "Shovel"
}
shovel_secret = {"Unlock Code": generate_unlock_code()}
client.write(record_type, shovel_secret, shovel_plain)

# Hammer
hammer_plain = {
    "Location": "Shed",
    "Storage": "Red Locked Tool Chest",
    "Tool": "Hammer"
}
hammer_secret = {"Unlock Code": generate_unlock_code()}
client.write(record_type, hammer_secret, hammer_plain)

# Drill
drill_plain = {
    "Location": "Garage",
    "Storage": "Black Locked Storage Box",
    "Tool": "Drill"
}

drill_secret = {"Unlock Code": generate_unlock_code()}
client.write(record_type, drill_secret, drill_plain)

# get all records of above type
print "Listing all records of type: {0}".format(record_type)
for record in client.query(record_type=[record_type]):
    record_json = record.json_serialize()
    tool_type = record_json['meta']['plain']['Tool']
    location = record_json['meta']['plain']['Location']
    storage = record_json['meta']['plain']['Storage']
    unlock_code = record_json['data']['Unlock Code']

    print "Tool: {0}, Location: {1}, Storage: {2}, Unlock Code: {3}".format(
        tool_type, location, storage, unlock_code)


print "\nListing all records that list the tool: Hammer"
basic_query = {
    'eq': {
        'name': 'Tool',
        'value': 'Hammer'
    }
}

hammer_query = client.query(plain=basic_query)
for record in hammer_query:
    record_json = record.json_serialize()
    tool_type = record_json['meta']['plain']['Tool']
    location = record_json['meta']['plain']['Location']
    storage = record_json['meta']['plain']['Storage']
    unlock_code = record_json['data']['Unlock Code']

    print "Tool: {0}, Location: {1}, Storage: {2}, Unlock Code: {3}".format(
        tool_type, location, storage, unlock_code)


print "\nListing all tools that are Shovels, and are also in the Shed:"
advanced_query = {
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
                'value': 'Shovel'
                },
        },
    ]
}

for record in client.query(plain=advanced_query):
    record_json = record.json_serialize()
    tool_type = record_json['meta']['plain']['Tool']
    location = record_json['meta']['plain']['Location']
    storage = record_json['meta']['plain']['Storage']
    unlock_code = record_json['data']['Unlock Code']

    print "Tool: {0}, Location: {1}, Storage: {2}, Unlock Code: {3}".format(
        tool_type, location, storage, unlock_code)
