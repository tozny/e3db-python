# types.py
import copy

class IncomingSharingPolicy():
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
        self.writer_id = json['writer_id']
        self.writer_name = json['writer_name']
        self.record_type = json['record_type']

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
            'writer_id': self.writer_id,
            'writer_name': self.writer_name,
            'record_type': self.record_type
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
        self.reader_id = json['reader_id']
        self.reader_name = json['reader_name']
        self.record_type = json['record_type']

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
            'reader_id': self.reader_id,
            'reader_name': self.reader_name,
            'record_type': self.record_type
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

        self.meta = meta
        # make copy of the data so we dont modify the original object passed in
        self.data = copy.deepcopy(data)

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
            'meta': self.meta.to_json(),
            'data': self.data
        }

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

        return self.meta

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

        return self.data

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

        self.meta = meta

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

        self.meta.update(meta.to_json())
        self.data = data

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
        self.writer_id = json['writer_id']
        self.user_id = json['user_id']
        self.record_type = str(json['type'])
        self.plain = json['plain']
        # optional, as some get set by the server
        # set these to None if they are not included when init is called.
        self.record_id = json['record_id'] if 'record_id' in json else None
        # datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.created = json['created'] if 'created' in json else None
        self.last_modified = json['last_modified'] if 'last_modified' in json else None
        self.version = json['version'] if 'version' in json else None

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

        return {
            'record_id': self.record_id,
            'writer_id': self.writer_id,
            'user_id': self.user_id,
            'type': self.record_type,
            'plain': self.plain,
            'created': self.created,
            'last_modified': self.last_modified,
            'version': self.version
        }

    def update(self, json):
        """
        Update the Meta object with new configuration.

        Configuration is taken in as a JSON-style dictionary object.

        Parameters
        ----------
        json : dict
            JSON key-value store of Meta data configuration.

        Returns
        -------
        None
        """

        self.record_id = json['record_id']
        self.writer_id = json['writer_id']
        self.user_id = json['user_id']
        self.record_type = json['type']
        self.plain = json['plain']
        self.created = json['created']
        self.last_modified = json['last_modified']
        self.version = json['version']

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
        self.__client_id = str(client_id)
        self.__public_key = public_key
        self.__validated = validated

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
            'client_id': self.__client_id,
            'public_key': self.__public_key,
            'validated': self.__validated
        }

    def public_key(self):
        """
        Public method to retrieve the public key of the client.

        Parameters
        ----------
        None

        Returns
        -------
        str
            Base64URL encoded string of bytes that is the client's public key.
        """

        return self.__public_key['curve25519']

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

        self.client_id = json['client_id']
        self.api_key_id = json['api_key_id']
        self.api_secret = json['api_secret']
        self.public_key = json['public_key']
        self.name = json['name']

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
            'client_id': self.client_id,
            'api_key_id': self.api_key_id,
            'api_secret': self.api_secret,
            'public_key': self.public_key,
            'name': self.name
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

        return (self.api_key_id, self.api_secret)

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
        return self.client_id

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
        return self.public_key['curve25519']

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
        return self.name

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

        self.query = query
        self.records = records

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

        return iter(self.records)

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

        return len(self.records)

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
        return self.query.get_after_index()

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
        self.count = count
        self.after_index = after_index
        self.include_data = include_data
        self.writer_ids = writer_ids
        self.user_ids = user_ids
        self.record_ids = record_ids
        self.content_types = content_types
        self.plain = plain
        self.include_all_writers = include_all_writers

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
        return self.after_index

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
            'count': self.count,
            'after_index': self.after_index,
            'include_data': self.include_data,
            'writer_ids': self.writer_ids,
            'user_ids': self.user_ids,
            'record_ids': self.record_ids,
            'content_types': self.content_types,
            'plain': self.plain,
            'include_all_writers': self.include_all_writers
        }
