class NoteOptions():
    
    def __init__(self, note_writer_client_id: str, max_views: int, id_string: str, expiration: str, 
                expires: bool, type: str, plain: dict, file_meta: dict, eacp=None):
        """
        Initializes the NoteOptions class. Represents optional values not necessary
        for creating a note. 

        NoteOptions are to be split into note-specific sub-types (premium, non-premium,
        anonymous) focused on how users use the SDK when notes reach that level of complexity. 

        Parameters
        ----------
        client_id : str


        max_views : int


        id_string : str


        expiration : Date


        expires : bool


        eacp : EACP 


        type : str


        plain : dict[string]string



        file_meta : dict[string]string 

        Returns
        -------
        None
        """

        # These may need to be typed properly! 

        # Premium options
        self.__note_writer_client_id    = note_writer_client_id
        self.__max_views                = max_views
        self.__expiration               = expiration # Type is RFC3339 string: datetime.datetime.utcnow().isoformat()
                                                     # User-provided? Or take a date and convert at serialization?
        self.__expires                  = expires
        self.__eacp                     = eacp
        self.__id_string                = id_string

        # Non-premium options
        self.__type          = type
        self.__plain         = plain
        self.__file_meta     = file_meta

    def to_json(self) -> dict:
        """
        Seriaizes the note as a JSON-style object.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            JSON-style document containing the Note elements
        """

        to_serialize = {
            'client_id': self.__note_writer_client_id,
            'max_views': self.__max_views,
            'expiration': self.__expiration,
            'expires': self.__expires,
            'eacp': self.__eacp,
            'id_string': self.__id_string,
            'type': self.__type,
            'plain': self.__plain,
            'file_meta': self.__file_meta
        }

        return to_serialize

    @staticmethod
    def decode(json):
        """
        Decodes a JSON response into a NoteOptions object. 

        Parameters
        ----------
        json : dict
            JSON data to be decoded into a NoteOptions object

        Returns
        -------
        note : e3db.NoteOptions
            A NoteOptions object that contains the contents from json 
        """
        client_id = json['client_id'] if 'client_id' in json else None
        max_views = json['max_views'] if 'max_views' in json else None
        expiration = json['expiration'] if 'expiration' in json else None
        expires = json['expires'] if 'expires' in json else False
        eacp = json['eacp'] if 'eacp' in json else None
        id_string = json['id_string'] if 'id_string' in json else None
        type = json['type'] if 'type' in json else None
        plain = json['plain'] if 'plain' in json else None
        file_meta = json['file_meta'] if 'file_meta' in json else None
        return NoteOptions(
            note_writer_client_id=client_id,
            max_views=max_views,
            id_string=id_string,
            expiration=expiration,
            expires=expires,
            type=type,
            plain=plain,
            file_meta=file_meta,
            eacp=eacp
        )

    @property
    def note_writer_client_id(self):
        return self.__note_writer_client_id

    @property
    def max_views(self):
        return self.__max_views

    @property
    def expiration(self):
        return self.__expiration

    @property
    def expires(self):
        return self.__expires

    @property
    def eacp(self):
        return self.__eacp

    @property
    def id_string(self):
        return self.__id_string

    @property
    def type(self):
        return self.__type

    @property
    def plain(self):
        return self.__plain

    @property
    def file_meta(self):
        return self.__file_meta
