import copy
from uuid import UUID
from .note_keys import NoteKeys
from .note_options import NoteOptions

class Note():
    def __init__(self, data: dict, note_keys: NoteKeys, note_options: NoteOptions):
        """
        Initialize the Note class

        Parameters
        ----------
        note_keys : note_keys.NoteKeys
            Key object that contains encryption, signing, and
            access keys. 

        note_options : note_options.NoteOptions
            Options object that contains optional values that
            are not required to create a note but provide 
            additional functionality. 

        Returns
        -------
        None

        """
        if note_keys and (not isinstance(note_keys, NoteKeys)):
            raise TypeError(f"NoteKey object is not e3db.NoteKeys type. Given type: {type(note_keys)}")
        else:
            self.__note_keys = note_keys
        if note_options and (not isinstance(note_options, NoteOptions)):
            raise TypeError(f"NoteOptions object is not e3db.NoteOptions type. Given type: {type(note_options)}")
        else:
            self.__note_options = note_options
        self.__eacp                          = None 
        self.__views                         = None
        self.__note_id                       = None
        self.__created_at                    = None 
        self.data                            = copy.deepcopy(data)

        # Signing makes sense to do after Note creation from a user's perspective.
        # Makes less sense to, say, "create this note with a signature you already have"
        # rather than "create a note, then sign it when you want to write it". 
        self.__signature                     = "" 

    def to_json(self):
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

        note_keys_decoded = self.__note_keys.to_json()
        note_options_decoded = self.__note_options.to_json()

        to_serialize = {
            'data': self.data,
            'signature': self.__signature,
            'note_id': self.__note_id,
            'created_at': self.__created_at,
            'mode': note_keys_decoded['mode'],
            'recipient_signing_key': note_keys_decoded['note_recipient_signing_key'],
            'writer_signing_key': note_keys_decoded['note_writer_signing_key'],
            'writer_encryption_key': note_keys_decoded['note_writer_encryption_key'],
            'encrypted_access_key': note_keys_decoded['encrypted_access_key'],
            'client_id': str(note_options_decoded['client_id']),
            'type': note_options_decoded['type'],
            'plain': note_options_decoded['plain'],
            'file_meta': note_options_decoded['plain'],
            'max_views': note_options_decoded['max_views'],
            'expiration': note_options_decoded['expiration'],
            'expires': note_options_decoded['expires'],
            'eacp': note_options_decoded['eacp'],
            'id_string': note_options_decoded['id_string']
        }

        return to_serialize

    @staticmethod
    def decode(json: dict):
        """
        Decodes a JSON response into a Note object. 

        Parameters
        ----------
        json : dict
            JSON data to be decoded into a Note object

        Returns
        -------
        note : e3db.Note
            A Note object that contains the contents from json 
        """
        data = json['data'] if 'data' in json else None
        note_options = NoteOptions.decode(json)
        note_keys = NoteKeys.decode(json)
        note = Note(data=data, note_keys=note_keys, note_options=note_options)

        signature = json['signature'] if 'signature' in json else None
        created_at = json['created_at'] if 'created_at' in json else None
        note_id = json['note_id'] if 'note_id' in json else None
        note.signature = signature
        note.created_at = created_at
        note.note_id = note_id
        return note

    @property 
    def signature(self) -> str:
        """
        Get signature.

        Parameters
        ----------
        None

        Returns
        -------
        signature : str
            The signature that signed the note
        """
        return self.__signature

    @signature.setter
    def signature(self, value):
        """
        Set signature.

        Paramters
        ---------
        value : str
            signature

        Returns
        -------
        None
        """
        self.__signature = value

    @property
    def created_at(self) -> str:
        """
        Get created_at.

        Parameters
        ----------
        None

        Returns
        -------
        created_at : str
            The time the note was created at
        """
        return self.__created_at

    @created_at.setter
    def created_at(self, value):
        """
        Set created_at

        Parameters
        ----------
        value : str
            created_at

        Returns
        -------
        None
        """
        self.__created_at = value

    @property
    def note_id(self) -> UUID:
        """
        Get note_id.

        Parameters
        ----------
        None

        Returns
        -------
        note_id : UUID
            A server defined id 
        """
        return self.__note_id

    @note_id.setter
    def note_id(self, value):
        """
        Sets note_id.

        Parameters
        ----------
        value : str
            note_id

        Returns
        -------
        None
        """
        self.__note_id = value

    def get_client_id(self):
        """
        Get the client id associated with the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        client_id : str

        """
        return self.__client_id

    def get_mode(self) -> str:
        """
        Get the mode of the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        mode : str

        """
        return self.__mode

    def get_recipient_signing_key(self) -> str:
        """
        Get the recipient's signing key associated with the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        recipient_signing_key : str

        """
        return self.__note_keys.note_recipient_signing_key

    def get_writer_signing_key(self) -> str:
        """
        Get the writer's signing key associated with the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        writer_signing_key : str

        """
        return self.__note_keys.note_writer_signing_key

    def get_writer_encryption_key(self) -> str:
        """
        Get the writer's encryption key associated with the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        writer_encryption_key : str

        """
        return self.__note_keys.note_writer_encryption_key

    def get_eak(self) -> str:
        """
        Get the encrypted access key associated with the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        encrypted_access_key : str

        """
        return self.__note_keys.encrypted_access_key

    def get_type(self) -> str:
        """
        Get the type of the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        type : str

        """
        return self.__note_options.type

    def get_data(self) -> dict:
        """
        Get the data from the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        data : dict
            JSON-style dictionary
        """
        return self.data

    def get_plain(self) -> dict:
        """
        Get the plain meta of the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        plain : dict
            JSON-style dictionary
        """
        return self.__note_options.plain

    def get_file_meta(self) -> dict:
        """
        Get the file metadata of the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        file_meta : dict
            JSON-style dictionary
        """
        return self.__note_options.file_meta
        
    def get_signature(self) -> str:
        """
        Get the signature associated with the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        signature : str
            TSV1 Signature
        """
        return self.__signature

    def get_max_views(self) -> int:
        """
        Get the max views of the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        max_views : int

        """
        return self.__note_options.max_views

    def get_views(self) -> int:
        """
        Get the current number of views of the note.

        Parameters
        ----------
        None

        Returns
        -------
        views : int 
        """
        return self.__views

    def get_expiration(self) -> str:
        """
        Get the expiration time of the Note. 

        Parameters
        ----------
        None

        Returns
        -------
        expiration : str
            RFC3339 String 
        """
        return self.__note_options.expiration

    def is_expired(self) -> bool:
        """
        Checks whether the note has expired.

        Parameters
        ----------
        None

        Returns
        -------
        expires : bool
            Truth value determining whether the note has expired
        """
        return self.__note_options.expires
        
    def get_eacp(self):
        return NotImplementedError
