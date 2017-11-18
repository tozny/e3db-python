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
    did_read = {}
    for record in client.query(record_type=record_types):
        print ("Confirming %s (%s)" % (record.meta.record_id, record.meta.record_type))
        assert record.data['test'] == record_data['test'], "(actual) %s, (expected) %s; (%s)" % (record.data['test'], record_data['test'], record.meta.record_type)
        assert record.data == record_data, "(actual) %s, (expected) %s; (%s)" % (record.data, record_data, record.meta.record_type)
        assert record.meta.plain == {}, "(actual) %s, (expected) %s; (%s)" % (record.meta.plain, {}, record.meta.record_type)
        did_read[record.meta.record_type] = True

    assert len(did_read) > 0, "Failed to read any records."
    assert all([x in did_read.keys() for x in record_types]), "Failed to read all record types. (actual) %s, (expected) %s" % (did_read.keys(), record_types)
        

def write(record_type):
    record = client.write(record_type, record_data)
    print ("Wrote %s (%s)." % (record.meta.record_id, record.meta.record_type))

def delete(record_types):
    for record in client.query(record_type=record_types):
        print "Deleting %s/%s (%s)" % (record.meta.record_id, record.meta.version, record.meta.record_type)
        client.delete(record.meta.record_id, record.meta.version)
    

def usage(err):
    if err:
        print err
        
    print '''
integration.py <command>

  Read, write and delete integration test records. This script uses
  the default credentials found at ~/.tozny/e3db.json.

where <command> is one of:

  read [type[, type, ...]]
    Read records of the given type(s). Multiple types should be
    provided in a comma separated list. An error will be raised if no
    record exists for a given type.

  write  
    Write a test record with the type 'python'.

  delete
    Delete all records of type 'python'.
    '''

    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage("Please provide a command")

    writer_record_type = 'python'
    method = sys.argv[1]

    if method == 'write':
        write(writer_record_type)
    elif method == 'read':
        # create a list of record types we should read
        if len(sys.argv) < 3:
            usage("Please provide record types in a comma-separated list.")

        if len(sys.argv) > 3:
            usage("Please provide only a comma-separated list of record types.")
            
        reader_record_types = sys.argv[2].split(',')
        if len(reader_record_types) == 0:
            usage("Please provide some record types to read.")

        read(reader_record_types)
    elif method == 'delete':
        delete(writer_record_type)

    sys.exit(0)
