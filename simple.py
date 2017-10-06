import e3db

conf = e3db.Config.load('dev')
client = e3db.Client(conf)
#client.debug()

test_type = 'Tools'

plain = {
    "Location": "Shed",
    "Storage": "Locked Tool Chest",
    "Tool": "Hammer"
}

secret = {
    "Unlock Code": "12345"
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
                'value': 'Hammer'
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
