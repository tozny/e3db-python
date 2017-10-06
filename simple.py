import e3db

def generate_unlock_code():
    # generate a secure random number for our tools combination lock.
    import os
    import random
    import sys
    csprng = random.SystemRandom()
    # 5 digit combo
    random_combo = csprng.randint(0, 99999)
    return '{:05d}'.format(random_combo)

conf = e3db.Config.load('dev')
client = e3db.Client(conf)
#client.debug()

test_type = 'Tools'

plain = {
    "Location": "Shed",
    "Storage": "Locked Tool Chest",
    "Tool": "Shovel"
}

secret = {
    "Unlock Code": generate_unlock_code()
}
record_id = client.write(test_type, secret, plain)
record = client.read(record_id)

# get all records of above type
for record in client.query(record_type=[test_type]):
    print record.json_serialize()['data']

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

basic_query = {
    'eq': {
        'name': 'Tool',
        'value': 'Hammer'
    }
}

tech = client.query(plain=basic_query)

print "Advanced query:"
for record in client.query(plain=advanced_query):
    print record.json_serialize()['data']
