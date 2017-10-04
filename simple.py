import e3db

conf = e3db.Config.load('dev')
client = e3db.Client(conf)
#client.debug()

client.write('test_type6', {"foo":"bar"}, {})
