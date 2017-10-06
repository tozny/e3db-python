import e3db

conf = e3db.Config.load('dev')
client = e3db.Client(conf)
#client.debug()

test_type = 'advice'

record_id = client.write(test_type, {"Secret":"There's always money in the banana stand."}, {})
record = client.read(record_id)

# get all records of above type
for record in client.query(record_type=[test_type]):
    print record.json_serialize()['data']

advanced_query = {
    'eq': {
        'name': 'house',
        'value': 'Stark'
    }

}

for record in client.query(advanced_query):
    print record.json_serialize()['data']
