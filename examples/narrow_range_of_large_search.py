import e3db
from e3db.types import Search
from e3db.types import Range
from datetime import datetime, timedelta
import json
import os
import time

max_records = 10000 # upper limit of allowed records
time_zone_offset = "-7:00" # PDT daylight saving offset from UTC
credentials_path = "credentials.json" # your e3db credentialss
output_path = "results.txt"

# Helper method to print and write to file.
def print_and_write(fp, message):
    print(message)
    fp.write(message + "\n")

# Helper method to write certain record data to file
def write_partial_record_data(fp, record):
    # Modify below to get more record information.
    # Properties detailed here: https://github.com/tozny/e3db-python/blob/master/e3db/types/record.py
    fp.write("{0} - {1}\n".format(record.meta.record_id, record.meta.last_modified))

# Helper method to write all available record data to file
def write_full_records(fp, record):
    fp.write(json.dumps(record.to_json())+"\n")

# Helper method to recursively query narrower time range,
# and write record information to file.
def query_narrow_time_range_and_write_to_file(fp, client, start, end, query):
    result = client.search(query)
    if result.total_results >= max_records:
        time_difference = end-start
        midpoint_time = start + time_difference/2
        ## Uncomment to see the progress on the query, spams terminal messages if records are sparse between time frames.
        # print("{0} total hits for time range {1} TO {2}: maximum is {3}. Narrowing Range to {4} TO {5} TO {6}\n".format(result.total_results, 
        #                                                                                                                     start, 
        #                                                                                                                     end, 
        #                                                                                                                     max_records, 
        #                                                                                                                     start, 
        #                                                                                                                     midpoint_time, 
        #                                                                                                                     end))
        query = query.range(start=start, end=midpoint_time, zone_offset=time_zone_offset)
        query.next_token = 0
        query_narrow_time_range_and_write_to_file(fp, client, start, midpoint_time, query)

        query.next_token = 0
        query = query.range(start=midpoint_time, end=end, zone_offset=time_zone_offset)
        query_narrow_time_range_and_write_to_file(fp, client, midpoint_time, end, query)
        return
    while True:
        print("Found {0} total records: grabbing {1} records from next_token {2}: in time range {3} to {4}\n".format(result.total_results, 
                                                                                                        len(result), 
                                                                                                        query.next_token, 
                                                                                                        start, 
                                                                                                        end))
        for r in result: # writes all records to file
            # write_full_records(fp, r) # uncomment me and comment out below to see full record meta.
            write_partial_record_data(fp, r)
        next_token = result.next_token
        if next_token == 0:
            break
        query.next_token = next_token 
        result = client.search(query)
    return

# Helper method to narrow our query recursively until we satisfy the max_records limit,
# and stores all of the results in list "all_results".
# Allows you to iterate through the results programmatically, but can be expensive if you expect a lot of records.
def query_narrow_time_range(client, start, end, query, all_results):
    result = client.search(query)
    if result.total_results >= max_records:
        time_difference = end-start
        midpoint_time = start + time_difference/2
        ### Uncomment to see the progress on the query, spams terminal messages if records are sparse between time frames.
        # print("{0} total hits for time range {1} TO {2}: maximum is {3}. Narrowing Range to {4} TO {5} TO {6}\n".format(result.total_results, 
        #                                                                                                                     start, 
        #                                                                                                                     end, 
        #                                                                                                                     max_records, 
        #                                                                                                                     start, 
        #                                                                                                                     midpoint_time, 
        #                                                                                                                     end))
        query = query.range(start=start, end=midpoint_time, zone_offset=time_zone_offset)
        query.next_token = 0
        query_narrow_time_range(client, start, midpoint_time, query, all_results)

        query.next_token = 0
        query = query.range(start=midpoint_time, end=end, zone_offset=time_zone_offset)
        query_narrow_time_range(client, midpoint_time, end, query, all_results)
        return
    while True:
        print("Found {0} total records: grabbing {1} records from next_token {2}: in time range {3} to {4}\n".format(result.total_results, 
                                                                                                        len(result), 
                                                                                                        query.next_token, 
                                                                                                        start, 
                                                                                                        end))
                                                                                    
        for r in result:
            all_results.append(r)
        next_token = result.next_token
        if next_token == 0:
            break
        query.next_token = next_token 
        result = client.search(query)
    return

def search_all_records():
    if os.path.exists(credentials_path):
        print("found", credentials_path)
        client = e3db.Client(json.load(open(credentials_path)))

        with open(output_path, 'w') as output_file:
            print_and_write(output_file, "Opening file to write to: {0}".format(output_path))
            print_and_write(output_file, "Running query for all records")
            
            # Keep the end time the same.
            # If you expect data coming in older than last year, increasing the days value in timedelta will query from an earlier time.
            # Narrowing the start time will speed up the search if you expect the range is too large.
            end_time = datetime.now() + timedelta(days=5)
            start_time = end_time - timedelta(days=365) 

            # E3db Search by default does not provide data. 
            # More examples and information can be found here https://github.com/tozny/e3db-python#searching-records.
            # If you want to include_data add in the flag include_data=True as shown below:
            # query = Search(include_data=True, include_all_writers=True, next_token=0, count=1000)

            query = Search(include_all_writers=True, next_token=0, count=1000)
            query_narrow_time_range_and_write_to_file(output_file, client, start_time, end_time, query)

            ### Demonstration of storing records in memory instead of writing to file
            # all_results = []
            # query_narrow_time_range(client, start_time, end_time, query, all_results)
            # for ar in all_results:
            #     write_full_records(output_file, ar)
    else:
        print("could not find credentials file at path: {0}".format(credentials_path))

if __name__ == "__main__":
    search_all_records()
