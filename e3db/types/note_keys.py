class NoteKeys():

    def __init__(self, mode: str, note_recipient_signing_key: str, note_writer_signing_key: str,
                note_writer_encryption_key: str, encrypted_access_key: str):
        """
        Initializes the NoteKeys class. Represents the keys used to encrypt and
        sign a note.

        Parameters
        ----------
        mode : str 
            The cryptographic mode (e.g. sodium, NIST)

        recipient_signing_key : str
            Recipients public signing key

        writer_signing_key : str
            Writer's public sigining key

        writer_encryption_key : str
            Writer's public encryption key

        encrypted_access_key : str
            Encrypted private access key

        Returns
        -------
        None
        """

        # These may need to be typed properly! (see e.g. meta.py)
        self.__mode                     = mode
        self.__note_recipient_signing_key    = note_recipient_signing_key
        self.__note_writer_signing_key       = note_writer_signing_key
        self.__note_writer_encryption_key    = note_writer_encryption_key
        self.__encrypted_access_key     = encrypted_access_key

    def to_json(self) -> dict:
        """
        Seriaizes the note keys as a JSON-style object.

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
            'mode': self.__mode,
            'note_recipient_signing_key': self.__note_recipient_signing_key,
            'note_writer_signing_key': self.__note_writer_signing_key,
            'note_writer_encryption_key': self.__note_writer_encryption_key,
            'encrypted_access_key': self.__encrypted_access_key
        }

        return to_serialize
