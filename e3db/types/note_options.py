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

        # Do key names need to match other SDKs to guarantee interoperability?
        to_serialize = {
            'note_writer_client_id': self.__note_writer_client_id,
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
