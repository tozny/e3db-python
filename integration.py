#! /usr/bin/env python

# run integration tests

import sys
import e3db

# Load default config in ~/.tozny/e3db.json
conf = e3db.Config.load()

# Now create a client using that configuration.
client = e3db.Client(conf)

record_data = {'test': 'Supercalifragilisticexpialidocious'}

def read(record_types):
    # read records from every sdk type
    for record in client.query(record_type=record_types):
        assert(record.data['test'] == record_data['test'])
        assert(record.data == record_data)

def write(record_type):
    record = client.write(record_type, record_data)

if __name__ == '__main__':
    writer_record_type = 'python'
    method = sys.argv[1]

    if method == 'write':
        write(writer_record_type)
    if method == 'read':
        # create a list of record types we should read
        reader_record_types = sys.argv[2].split(',')
        read(reader_record_types)
