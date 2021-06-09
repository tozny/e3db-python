import base64
from hashlib import blake2b
import nacl.hash
import nacl.encoding

BLAKE2B_HASHER = nacl.hash.blake2b

class BaseCrypto:
    @classmethod
    def get_mode(self):
        pass

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        pass

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        pass

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        pass

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        pass

    @classmethod
    def decode_public_key(self, key):
        pass

    @classmethod
    def encode_public_key(self, key):
        pass

    @classmethod
    def decode_private_key(self, key):
        pass

    @classmethod
    def encode_private_key(self, key):
        pass

    @classmethod
    def random_key(self):
        pass

    @classmethod
    def random_nonce(self):
        pass

    @classmethod
    def generate_keypair(self):
        # return public, private
        pass

    @staticmethod
    def to_bytes(b):
        if type(b) is bytes:
            return b
        elif type(b) is str:
            return bytes(b, "utf-8")
        else:
            return bytes(b)

    @classmethod
    def base64decode(self, s):
        # From https://stackoverflow.com/a/9956217
        # Python base64 implementation requires padding, which may not be present in the
        # encoded public/private keypair
        b = BaseCrypto.to_bytes(s)
        return base64.urlsafe_b64decode(b + b'=' * (4 - len(s) % 4))

    @classmethod
    def base64encode(self, s):
        # Encodes a utf-8/ascii bytes into  base 64 encoded bytes
        # remove "=" padding for general SDK compatibility
        b = BaseCrypto.to_bytes(s)
        return base64.urlsafe_b64encode(b).strip(b'=')

    @classmethod
    def encrypt_file(self, plaintext_file, key):
        pass

    @classmethod
    def decrypt_file(self, encrypted_file, destination_file, key):
        pass

    @classmethod
    def hashString(self, toHash: str) -> bytes:
        """
        Returns the raw encoded bytes of the hash of toHash string. 

        Parameters
        ----------
        toHash : str

        Returns
        -------
        bytes
            Byte hash of string. 
        """
        return BLAKE2B_HASHER(toHash.encode("utf-8"), encoder=nacl.encoding.RawEncoder)

    @classmethod
    def base64HashString(self, toHash: str) -> bytes:
        """
        Returns the Base64 encoded bytes of the hash of toHash string. 

        Parameters
        ----------
        toHash : str

        Returns
        -------
        bytes
            Byte hash of string. 
        """
        return BLAKE2B_HASHER(toHash.encode("utf-8"), encoder=nacl.encoding.Base64Encoder)

    @classmethod
    def hashMessage(self, toHash):
        """
        Returns the Base64 encoded bytes of the hash of toHash string. 

        Parameters
        ----------
        toHash : str

        Returns
        -------
        bytes
            Base64 encoded hash of string. 
        """

        hashed_message = self.hashString(toHash)
        return self.base64encode(hashed_message)

    @classmethod
    def verify(self, signature, message, public_key):
        pass

    @classmethod
    def decrypt_field(self, encrypted_field, ak):
        pass

    @classmethod
    def decrypt_note_eak(self, reader_key, encrypted_ak, writer_key):
        """
        Returns the decrypted access key as bytes. 

        Parameters
        ----------
        reader_key : str

        encrypted_ak : str

        writer_key : str

        Returns
        -------
        bytes
            Raw access key which is used for decryption. 
        """

        public_key = self.decode_public_key(writer_key)
        private_key = self.decode_private_key(reader_key)
        eak_fields = encrypted_ak.split(".")
        eak = self.base64decode(eak_fields[0])
        nonce = self.base64decode(eak_fields[1])
        return self.decrypt_eak(private_key, public_key, eak, nonce)
