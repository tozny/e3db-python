import base64
import copy
from hashlib import blake2b
from os import system
from uuid import uuid4
import nacl.hash
import nacl.encoding

BLAKE2B_HASHER = nacl.hash.blake2b
SIGNATURE_VERSION = 'e7737e7c-1637-511e-8bab-93c4f3e26fd9'  

class BaseCrypto:
    @classmethod
    def get_mode(self):
        pass

    @classmethod
    def get_signature_version(self):
        """
        Gets the signature version that is supported for Crypto. 

        Returns
        -------
        str
            The current signature version is uuid-v5 format. 
        """   

        return SIGNATURE_VERSION

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

    @classmethod
    def encrypt_note_ak(self, private_key, public_key, ak):
        """ A Wrapper function for obtaining an encrypted access key, generates a nonce
        and then calls the library specific version of encrypt_ak, and composes the expected 
        return type.

        Parameters
        ----------
        private_key : Base64UrlEncoded String of Bytes
            The sender's private encryption key
        public_key : Base54UrlEncoded String of Bytes
            The reader's public encryption key
        ak : str
            The access key to be encrypted

        Returns
        -------
        bytes
            The encrypted access key which is used for decryption, base64 encoded,
            in the form {nonce}.{eak}
        """
        nonce = self.random_nonce()
        mssg_obj = self.encrypt_ak(self.decode_private_key(private_key),
                               self.decode_public_key(public_key),
                               ak,
                               nonce)
        encoded_nonce = self.base64encode(mssg_obj.nonce).decode('utf-8')
        encoded_ciphertext = self.base64encode(mssg_obj.ciphertext).decode('utf-8')
        return f'{encoded_ciphertext}.{encoded_nonce}'

    @classmethod
    def encrypt_note(self, note, access_key, signing_key):
        """Encrypt and sign all of the data fields in a note object.

        Parameters
        ----------
        note : Note
            The note object that has un-encrypted data.
        access_key : str 
            The raw access key to use in encryption
        signing_key : str 
            The base64url encoded singing key used to sign each field.
   
        Returns
        -------
            a new note object with all the data fields encrypted and signed.
        """
        encrypted_note = copy.deepcopy(note)
        signature_salt = uuid4()
        # Note the salt is the payload in this field
        note_signature = self.sign_field('signature', signature_salt, signing_key)
        encrypted_note.signature = note_signature
        for key, value in note.data.items():
            signed_field = self.sign_field(key, value, signing_key, signature_salt)
            encrypted_note.data[key] = self.encrypt_field(signed_field, access_key)
        return encrypted_note

    @classmethod
    def sign_field(self, key, value, signing_key, object_salt=None):
        """ Returns a base64 encoded string """
        salt = object_salt if object_salt else uuid4()
        message = self.hashMessage("{}{}{}".format(salt, key, value))
        raw_key = self.base64decode(signing_key)
        raw_signature = self.sign_string(message, raw_key)
        signature = self.base64encode(raw_signature).decode('utf-8')
        length = len(signature)
        return f'{SIGNATURE_VERSION};{salt};{length};{signature}{value}'
