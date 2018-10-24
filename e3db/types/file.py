from datetime import datetime
import uuid


class File():

    def __init__(self, checksum, compression, size, writer_id, user_id,
        record_type, file_url=None, file_name=None, record_id=None,
        created=None, last_modified=None, version=None, plain={}):
        """
        Initialize the e3db.File class.

        Parameters
        ----------
        TODO

        Returns
        -------
        None
        """
        # required parameters
        # Data always empty dict, since data is stored on separate storage server
        self.__data = {}
        self.__writer_id = writer_id
        self.__user_id = user_id
        self.__record_type = str(record_type)
        self.__checksum = str(checksum)
        self.__compression = str(compression)
        self.__size = int(size)
        # optional, as some get set by the server
        # set these to None if they are not included when init is called.
        if record_id is not None:
            self.__record_id = uuid.UUID(record_id)
        else:
            self.__record_id = None
        # Have to check if specified or else we may end up with the string 'None'
        #>>> str(None)
        #'None'
        self.__file_url = str(file_url) if file_url is not None else None
        self.__file_name = str(file_name) if file_name is not None else None

        # When "printing" the timestamp (or converting to str), the T and Z characters are removed
        # Therefore, we need to parse both formats.
        try:
            self.__created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%fZ') if created is not None else None
        except ValueError:
            self.__created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S.%f') if created is not None else None
        try:
            self.__last_modified = datetime.strptime(last_modified, '%Y-%m-%dT%H:%M:%S.%fZ') if last_modified is not None else None
        except ValueError:
            self.__last_modified = datetime.strptime(last_modified, '%Y-%m-%d %H:%M:%S.%f') if last_modified is not None else None

        self.__version = str(version) if version is not None else None
        self.__plain = plain

    # writer_id getters and setters
    @property
    def writer_id(self):
        """
        Get writer_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            writer_id
        """
        return self.__writer_id

    @writer_id.setter
    def writer_id(self, value):
        """
        Set writer_id

        Parameters
        ----------
        value : uuid.UUID
            writer id

        Returns
        -------
        None
        """
        self.__writer_id = value

    # user_id getters and setters
    @property
    def user_id(self):
        """
        Get user_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            user_id
        """
        return self.__user_id

    @user_id.setter
    def user_id(self, value):
        """
        Set user_id

        Parameters
        ----------
        value : uuid.UUID
            user_id

        Returns
        -------
        None
        """
        self.__user_id = value

    # record_type getters and setters
    @property
    def record_type(self):
        """
        Get record_type

        Parameters
        ----------
        None

        Returns
        -------
        str
            record type
        """
        return self.__record_type

    @record_type.setter
    def record_type(self, value):
        """
        Set record_type

        Parameters
        ----------
        value : str
            record_type

        Returns
        -------
        str
            record type
        """
        self.__record_type = value

    # plain getters and setters
    @property
    def plain(self):
        """
        Get plaintext metadata

        Parameters
        ----------
        None

        Returns
        -------
        dict
            plaintext metadata
        """
        return self.__plain

    @plain.setter
    def plain(self, value):
        """
        Set plaintext metadata

        Parameters
        ----------
        value : dict
            plaintext metadata

        Returns
        -------
        None
        """
        self.__plain = value

    # record_id getters
    @property
    def record_id(self):
        """
        Get record_id

        Parameters
        ----------
        None

        Returns
        -------
        uuid.UUID
            record_id
        """
        return self.__record_id

    @record_id.setter
    def record_id(self, value):
        """
        Set record_id

        Parameters
        ----------
        value : str
            record_id

        Returns
        -------
        None
        """
        self.__record_id = uuid.UUID(record_id)

    # created getters
    @property
    def created(self):
        """
        Get created time of record.

        Parameters
        ----------
        None

        Returns
        -------
        datetime
            Time record was created.
        """
        return self.__created

    # last_modified getters
    @property
    def last_modified(self):
        """
        Get last_modified time of record.

        Parameters
        ----------
        None

        Returns
        -------
        datetime
            Time record was last_modified.
        """
        return self.__last_modified

    # version getters
    @property
    def version(self):
        """
        Get version of record.

        Parameters
        ----------
        None

        Returns
        -------
        str
            version of the record type
        """
        return self.__version

    # checksum getters
    @property
    def checksum(self):
        """
        Get checksum

        Parameters
        ----------
        None

        Returns
        -------
        str
            checksum
        """
        return self.__checksum

    # compression getters
    @property
    def compression(self):
        """
        Get compression

        Parameters
        ----------
        None

        Returns
        -------
        str
            compression
        """
        return self.__compression

    # size getters
    @property
    def size(self):
        """
        Get size of file in bytes

        Parameters
        ----------
        None

        Returns
        -------
        int
            size
        """
        return self.__compression

    # file_url getters and setters
    @property
    def file_url(self):
        """
        Get file_url

        Parameters
        ----------
        None

        Returns
        -------
        str
            file_url
        """
        return self.__file_url

    @file_url.setter
    def file_url(self, value):
        """
        Set file_url

        Parameters
        ----------
        value : str
            file_url

        Returns
        -------
        None
        """
        self.__file_url = str(value)

    # file_name getters and setters
    @property
    def file_name(self):
        """
        Get file_name

        Parameters
        ----------
        None

        Returns
        -------
        str
            file_name
        """
        return self.__file_name

    @file_name.setter
    def file_name(self, value):
        """
        Set file_name

        Parameters
        ----------
        value : str
            file_name

        Returns
        -------
        None
        """
        self.__file_name = str(value)

    def remove_empty(self, serialize):
        """
        Remove empty None objects during serialization
        """
        for key, value in serialize.items():
            if isinstance(value, dict):
                self.remove_empty(value)
            elif value is None or value == 'None':
                del serialize[key]
        return serialize

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
            'meta': {
                'record_id': str(self.__record_id),
                'writer_id': str(self.__writer_id),
                'user_id': str(self.__user_id),
                'type': str(self.__record_type),
                'created': str(self.__created),
                'last_modified': str(self.__last_modified),
                'version': str(self.__version),
                'file_meta': {
                    'file_url': str(self.__file_url),
                    'file_name': str(self.__file_name),
                    'checksum': str(self.__checksum),
                    'compression': str(self.__compression),
                    'size': int(self.__size)
                },
                'plain': self.__plain,
            },
            'data': self.__data,
        }

        # remove None (JSON null) objects
        return self.remove_empty(to_serialize)
