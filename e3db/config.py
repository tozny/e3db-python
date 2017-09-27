import json
import os

class Config:

    def __load_file(self, filename):
        '''
        Reads file from disk, and returns the json object as a dict
        '''
        try:
            with open(filename) as e3db_config:
                data = json.load(e3db_config)
            return data
        except ValueError as error:
            print "Loading E3DB json file failed. Perhaps the JSON is malformed?"
            print "Error: " + str(error)

    def load(self, profile=''):
        # if profile is empty we read the default ~/.tozny/e3db.json file
        home = os.path.expanduser('~')
        return self.__load_file(os.path.join(home, '.tozny',  profile, 'e3db.json'))
