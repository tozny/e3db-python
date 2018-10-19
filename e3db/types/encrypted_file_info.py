class EncryptedFileInfo(object):
    """
    Basic data structure to hold information about an Encrypted File
    """
    def __init__(self, url, md5, size):
        """
        Initialize the EncryptedFileInfo class.

        Parameters
        ----------
        json : dict
            Dictionary including writer_id, writer_name, and record_type.

        Returns
        -------
        None
        """

        # Will throw exception if UUID is malformed
        self.__url = url
        self.__md5 = md5
        self.__size = int(size)

    @property
    def url(self):
        """
        Get url

        Parameters
        ----------
        None

        Returns
        -------
        str
            url
        """
        return self.__url

    @property
    def md5(self):
        """
        Get md5

        Parameters
        ----------
        None

        Returns
        -------
        str
            md5
        """
        return self.__md5

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
        return self.__size
