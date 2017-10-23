# types.py
import copy
import uuid
from datetime import datetime

class IncomingSharingPolicy(object):
    """
    Class to create Incoming Sharing policy object.

    This class is a data holding class, similar to a C-style struct.
    """

    def __init__(self, json):
        """
        Initialize the Config class.

        Parameters
        ----------
        json : dict
            Dictionary including writer_id, writer_name, and record_type.

        Returns
        -------
        None
        """

        # Will throw exception if UUID is malformed
        self.__writer_id = uuid.UUID(json['writer_id'])
        self.__writer_name = str(json['writer_name'])
        self.__record_type = str(json['record_type'])

    # writer_id getters
    @property
    def writer_id(self):
        return self.__writer_id

    # writer_name getters
    @property
    def writer_name(self):
        return self.__writer_name

    # record_type getters
    @property
    def record_type(self):
        return self.__record_type

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Policy elements.
        """
        return {
            'writer_id': str(self.writer_id),
            'writer_name': str(self.writer_name),
            'record_type': str(self.record_type)
        }

class OutgoingSharingPolicy():
    def __init__(self, json):
        """
        Initialize the OutgoingSharingPolicy class.

        Parameters
        ----------
        json : dict
            Dictionary including reader_id, reader_name, and record_type.

        Returns
        -------
        None
        """
        self.__reader_id = uuid.UUID(json['reader_id'])
        self.__reader_name = str(json['reader_name'])
        self.__record_type = str(json['record_type'])

    # reader_id getters
    @property
    def reader_id(self):
      return self.__reader_id

    # reader_name getters
    @property
    def reader_name(self):
      return self.__reader_name

    # record_type getters
    @property
    def record_type(self):
        return self.__record_type

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Policy elements.
        """

        return {
            'reader_id': str(self.__reader_id),
            'reader_name': str(self.__reader_name),
            'record_type': str(self.__record_type)
        }

class Record():
    def __init__(self, meta=None, data=None):
        """
        Initialize the Record class.

        Parameters
        ----------
        meta : e3db.Meta
            Meta data object to include with the record.
            Required.

        data : dict
            JSON key-value store of data to be encrypted.

        Returns
        -------
        None
        """

        # Check that meta being passed in is of e3db.Meta type.
        if meta and (not isinstance(meta, Meta)):
            raise TypeError("Meta object is not e3db.Meta type. Given type: {0}".format(type(meta)))
        else:
            self.__meta = meta

        # Check that data passed in is a dictionary
        if data and (not isinstance(data, dict)):
            raise TypeError("Data object is not dict. Given type: {0}".format(type(data)))

        # make copy of the data so we dont modify the original object passed in
        self.__data = copy.deepcopy(data)

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Record elements.
        """

        return {
            'meta': self.__meta.to_json(),
            'data': self.__data
        }

    # meta getters and setters
    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self, value):
        self.__meta = value

    # data getters and setters
    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    def get_meta(self):
        """
        Get Meta object from the Record.

        Parameters
        ----------
        None

        Returns
        -------
        e3db.Meta
            Meta from the Record.
        """

        return self.__meta

    def get_data(self):
        """
        Get data dict from the Record.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style key-value pairs of the plaintext data
        """

        return self.__data

    def update_meta(self, meta):
        """
        Update Meta object of the Record.

        Parameters
        ----------
        meta : e3db.Meta
            Meta from the Record.

        Returns
        -------
        None
        """

        self.__meta = meta

    def update(self, meta, data):
        """
        Update entire Record object.

        Replaces current meta and data with passed in data.

        Parameters
        ----------
        meta : e3db.Meta
            Meta from the Record.

        data : dict
            JSON-style key-value pairs of the plaintext data

        Returns
        -------
        None
        """

        self.__meta = meta
        self.__data = data

class Meta():
    def __init__(self, json):
        """
        Initialize the Meta class.

        If certain keys, such as record_id, created, last_modified, and version
        are not missing (such as when a record is created, but these variables
        have not been set by the server yet).

        Parameters
        ----------
        json : dict
            JSON key-value store of Meta data configuration.

        Returns
        -------
        None
        """
        # required
        self.__writer_id = uuid.UUID(json['writer_id'])
        self.__user_id = uuid.UUID(json['user_id'])
        self.__record_type = str(json['type'])
        self.__plain = json['plain'] if 'plain' in json else None
        # optional, as some get set by the server
        # set these to None if they are not included when init is called.
        #self.record_id = json['record_id'] if 'record_id' in json else None
        if 'record_id' in json:
            if json['record_id'] != None and json['record_id'] != str(None):
                self.__record_id = uuid.UUID(json['record_id'])
            else:
                self.__record_id = json['record_id']
        else:
            self.__record_id = str(None)

        # When "printing" the timestamp (or converting to str), the T and Z characters are removed
        # Therefore, we need to parse both formats.
        try:
            self.__created = datetime.strptime(json['created'], '%Y-%m-%dT%H:%M:%S.%fZ') if 'created' in json else None
        except ValueError:
            self.__created = datetime.strptime(json['created'], '%Y-%m-%d %H:%M:%S.%f') if 'created' in json else None
        try:
            self.__last_modified = datetime.strptime(json['last_modified'], '%Y-%m-%dT%H:%M:%S.%fZ') if 'last_modified' in json else None
        except ValueError:
            self.__last_modified = datetime.strptime(json['last_modified'], '%Y-%m-%d %H:%M:%S.%f') if 'last_modified' in json else None

        self.__version = json['version'] if 'version' in json else None

    # writer_id getters and setters
    @property
    def writer_id(self):
        return self.__writer_id

    @writer_id.setter
    def writer_id(self, value):
        self.__writer_id = value

    # user_id getters and setters
    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        self.__user_id = value

    # record_type getters and setters
    @property
    def record_type(self):
        return self.__record_type

    @record_type.setter
    def record_type(self, value):
        self.__record_type = value

    # plain getters and setters
    @property
    def plain(self):
        return self.__plain

    @plain.setter
    def plain(self, value):
        self.__plain = value

    # record_id getters
    @property
    def record_id(self):
        return self.__record_id

    # created getters
    @property
    def created(self):
        return self.__created

    # last_modified getters
    @property
    def last_modified(self):
        return self.__last_modified

    # version getters
    @property
    def version(self):
        return self.__version

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Meta elements.
        """

        to_serialize = {
            'record_id': str(self.__record_id),
            'writer_id': str(self.__writer_id),
            'user_id': str(self.__user_id),
            'type': str(self.__record_type),
            'plain': self.__plain,
            'created': str(self.__created),
            'last_modified': str(self.__last_modified),
            'version': str(self.__version)
        }

        # remove None (JSON null) objects
        for key,value in to_serialize.items():
            if value == None or value == 'None':
                del to_serialize[key]

        return to_serialize

class ClientInfo():
    def __init__(self, client_id, public_key, validated):
        """
        Initialize the ClientInfo class.

        If certain keys, such as record_id, created, last_modified, and version
        are not missing (such as when a record is created, but these variables
        have not been set by the server yet).

        Parameters
        ----------
        client_id : str
            UUID of the client

        public_key : dict
            Type of key, and Base64URL encoded string of bytes that is the
            client's public key.

        validated : bool
            Whether then client has been validated or not.

        Returns
        -------
        None
        """
        self.__client_id = uuid.UUID(client_id)
        self.__public_key = dict(public_key)
        self.__validated = bool(validated)

    # client_id getters
    @property
    def client_id(self):
        return self.__client_id

    # public_key getters
    @property
    def public_key(self):
        return self.__public_key['curve25519']

    # validated getters
    @property
    def validated(self):
        return self.__validated

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the ClientInfo elements.
        """

        return {
            'client_id': str(self.__client_id),
            'public_key': dict(self.__public_key),
            'validated': bool(self.__validated)
        }

class ClientDetails():
    def __init__(self, json):
        """
        Initialize the ClientDetails class.

        Parameters
        ----------
        json : dict
            Configuration including keys for client_id, api_key_id, api_secret,
            public_key, and name.

        Returns
        -------
        None
        """

        self.__client_id = uuid.UUID(json['client_id'])
        self.__api_key_id = str(json['api_key_id'])
        self.__api_secret = str(json['api_secret'])
        self.__public_key = dict(json['public_key'])
        self.__name = str(json['name'])

    # client_id getters
    @property
    def client_id(self):
        return self.__client_id

    # api_key_id getters
    @property
    def api_key_id(self):
        return self.__api_key_id

    # api_secret getters
    @property
    def api_secret(self):
        return self.__api_secret

    # public_key getters
    @property
    def public_key(self):
        return self.__public_key['curve25519']

    # name getters and setters
    @property
    def name(self):
        return self.__name

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the ClientDetails elements.
        """
        return {
            'client_id': str(self.__client_id),
            'api_key_id': str(self.__api_key_id),
            'api_secret': str(self.__api_secret),
            'public_key': dict(self.__public_key),
            'name': str(self.__name)
        }

    def get_api_credentials(self):
        """
        Public method to retrieve the api credentials of the client.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            (api_key_id, api_secret) api credentials as strings
        """

        return (self.__api_key_id, self.__api_secret)

    def get_client_id(self):
        """
        Public method to retrieve the client_id of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            client_id (UUID)
        """
        return str(self.__client_id)

    def get_public_key(self):
        """
        Public method to retrieve the public key of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            client_id (UUID)
        """
        return self.__public_key['curve25519']

    def get_name(self):
        """
        Public method to retrieve the name of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            client name
        """
        return self.__name

class QueryResult():

    def __init__(self, query, records):
        """
        Initialize the QueryResult class.

        This object type is used as a storage for the results of an E3DB query.
        The main purpose is to allow iteration over a list of returned records
        that are the result of a Query operation.

        Parameters
        ----------
        query : e3db.Query
            Query object stored for later operations, such as looking up the
            after index returned from the server during query execution.

        records : list<e3db.Record>
            A list of records to store for later iteration and operations.

        Returns
        -------
        None
        """

        if query and (not isinstance(query, Query)):
            raise TypeError("Query object is not e3db.Query type. Given type: {0}".format(type(query)))
        else:
            self.__query = query

        # Check that all records in this list are of type e3db.Record
        if records and (not all(isinstance(x, Record) for x in records)):
            raise TypeError("Records should be a list of e3db.Record types. Given type: {0}".format(type(records)))
        else:
            self.__records = records

    # after_index getters and setters
    @property
    def after_index(self):
        return self.__query.after_index

    def __iter__(self):
        """
        Iterate over record objects.

        Parameters
        ----------
        None

        Returns
        -------
        iter
            Iterator over record objects returned from the Query.
        """

        return iter(self.__records)

    def __len__(self):
        """
        Get amount of records returned from the Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Amount of records returned from the Query.
        """

        return len(self.__records)

    def get_after_index(self):
        """
        Get after_index of records returned from the Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            After index returned from the Query after running against the
            E3DB server.
        """
        return self.__query.get_after_index()

class Query():

    def __init__(self, count, after_index=0, include_data=False, \
        writer_ids=None, user_ids=None, record_ids=None, content_types=None, \
        plain={}, include_all_writers=False):
        """
        Initialize the Query class.

        This object type is used to build a Query to run against the server.
        It is exposed through the e3db.Client.query method.

        Parameters
        ----------
        count : int
            How many records to include.

        after_index : int
            Where to start the query at. The server returns indicies which can
            be used to mark a query, so another query can be done, including the
            after_index to pick up where the other left off. Useful for batch
            and large jobs.
            Optional.

        include_data : bool
            Whether to include data, or just meta data when retrieving the
            E3DB records.
            Optional.

        writer_ids : list
            A list of writer_ids to use for filtering.
            Optional.

        user_ids : list
            A list of user_ids to use for filtering.
            Optional.

        record_ids : list
            A list of record_ids to lookup and use for filtering results.
            Optional.

        content_types : list
            A list of record types to use for filtering.
            Optional.

        plain : dict
            A JSON-style dictionary of a plaintext meta data query to use for
            filtering based on plaintext metadata of the Records.

        include_all_writers : bool
            Whether or not to include all writers, or just the writer_id of the
            client.

        Returns
        -------
        None
        """
        self.__count = int(count)
        self.__after_index = int(after_index)
        self.__include_data = bool(include_data)
        self.__writer_ids = [uuid.UUID(i) for i in writer_ids]
        self.__user_ids = [uuid.UUID(i) for i in user_ids]
        self.__record_ids = [uuid.UUID(i) for i in record_ids]
        self.__content_types = [str(i) for i in content_types]
        self.__plain = dict(plain) if plain != None else None
        self.__include_all_writers = bool(include_all_writers)

    # count getters
    @property
    def count(self):
        return self.__count

    # after_index getters
    @property
    def after_index(self):
        return self.__after_index

    # include_data getters
    @property
    def include_data(self):
        return self.__include_data

    # writer_ids getters
    @property
    def writer_ids(self):
        return self.__writer_ids

    # user_ids getters
    @property
    def user_ids(self):
        return self.__user_ids

    # record_ids getters
    @property
    def record_ids(self):
        return self.__record_ids

    # content_types getters
    @property
    def content_types(self):
        return self.__content_types

    # plain getters
    @property
    def plain(self):
        return self.__plain

    # include_all_writers getters
    @property
    def include_all_writers(self):
        return self.__include_all_writers

    def get_after_index(self):
        """
        Get after_index of records returned from the Query.

        Parameters
        ----------
        None

        Returns
        -------
        int
            After index returned from the Query after running against the
            E3DB server.
        """
        return self.__after_index

    def to_json(self):
        """
        Serialize the configuration as JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Query elements.
        """
        return {
            'count': int(self.__count),
            'after_index': int(self.__after_index),
            'include_data': bool(self.__include_data),
            'writer_ids': [str(i) for i in self.__writer_ids],
            'user_ids': [str(i) for i in self.__user_ids],
            'record_ids': [str(i) for i in self.__record_ids],
            'content_types': [str(i) for i in self.__content_types],
            'plain': self.__plain,
            'include_all_writers': bool(self.__include_all_writers)
        }
