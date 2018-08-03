from contextlib import contextmanager

class File():
    """
    Represents a large file stored on the server. This class can be used
    to both upload and download large files.
    """

    def __init__(self, filename, file):
       """
       Initialize the File class.

       Parameters
       ----------
       filename : String
           Name of the file (excluding path).

       file: file
           file-like object representing the plaintext contents of the file.
       """
       pass
       
    @property
    def filename(self):
       """Name of the file."""
       pass
    
    @property
    def md5(self):
       """MD5 Hash for the file's contents (after encryption)."""
       pass
    
    @contextmanager
    @property
    def file(self):
       """Underlying file-like object containing the file's plaintext contents. Note that this
       method should be called using the `with` statement, in order to properly manage the
       underlying file resource."""
       pass
