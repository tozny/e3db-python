import e3db

conf = e3db.Config.load('dev')
client = e3db.Client(conf)
#client.debug()

record_id = client.write('test_type6', {"foo":"bar"}, {})
record = client.read(record_id)

print record.json_serialize()['data']
import pdb; pdb.set_trace()
