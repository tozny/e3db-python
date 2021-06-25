from .base_crypto import BaseCrypto
import nacl.utils
import nacl.secret
import nacl.public
import nacl.bindings
import nacl.signing
import os.path
import hashlib
import base64
import tempfile

BLOCK_SIZE = 65536
SECRET_STREAM_TAG_MESSAGE = 0x0
TAG_FINAL = nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_FINAL
TAG_MESSAGE = nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE
ABYTES = nacl.bindings.crypto_secretstream_xchacha20poly1305_ABYTES
FILE_VERSION = 3


class SodiumCrypto(BaseCrypto):

    @classmethod
    def get_mode(self):
        return 'sodium'

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        return self.secret_box(ak).encrypt(BaseCrypto.to_bytes(plain), nonce)

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        return self.secret_box(ak).decrypt(ciphertext, nonce)

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        return self.box(private_key, public_key).encrypt(ak, nonce)

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        return self.box(private_key, public_key).decrypt(eak, nonce)

    @classmethod
    def box(self, private_key, public_key):
        return nacl.public.Box(private_key, public_key)

    @classmethod
    def secret_box(self, key):
        return nacl.secret.SecretBox(key)

    @classmethod
    def decode_public_key(self, key):
        return nacl.public.PublicKey(BaseCrypto.base64decode(key))

    @classmethod
    def encode_public_key(self, key):
        return BaseCrypto.base64encode(key)

    @classmethod
    def decode_private_key(self, key):
        return nacl.public.PrivateKey(BaseCrypto.base64decode(key))

    @classmethod
    def encode_private_key(self, key):
        return BaseCrypto.base64encode(key)

    @classmethod
    def random_key(self):
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    @classmethod
    def random_nonce(self):
        return nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    @classmethod
    def generate_keypair(self):
        # return public, private
        key = nacl.public.PrivateKey.generate()
        return key.public_key, key

    @classmethod
    def generate_signing_keypair(self):
        """
        Generates a SigningKey object and returns the associated public and
        private signing keys.

        Parameters
        ----------
        None

        Returns
        -------
        public_signing_key : nacl.signing.SigningKey.VerifyKey
            Public component of signing key.

        private_signing_key : nacl.signing.SigningKey.
            Private component of signing key. 
        """
        signing_key = nacl.signing.SigningKey.generate()
        return signing_key.verify_key, signing_key._signing_key

    @classmethod
    def generate_signing_key(self, key: bytes):
        """
        Generate a SigningKey object from a private signing key.

        Parameters
        ----------
        key : bytes
            Raw bytes of a private signing key. 

        Returns:
        nacl.signing.SigningKey
            Instance of the SigningKey class.
        """
        return nacl.signing.SigningKey(key)

    @classmethod
    def derive_public_signing_key(self, key: bytes):
        """
        Derives a public signing key from a given private signing key.

        Parameters
        ----------
        key : bytes
            Raw bytes of a private signing key.

        Returns
        -------
        VerifyKey
            Instance of VerifyKey that holds the derived public signing key.
        """
        signing_key = self.generate_signing_key(key)
        return signing_key.verify_key

    @classmethod
    def sign_string(self, string_to_sign: bytes, key: bytes) -> bytes:
        """
        Signs a message based on the signing key generated with a private signing key.

        Parameters
        ----------
        string_to_sign : bytes
            Raw bytes of the hash of the message being signed.
        
        key : bytes
            Raw bytes of a private signing key.

        Returns
        -------
        signature : bytes
            Signature in raw bytes
        """
        signing_key = self.generate_signing_key(key[:32])
        return signing_key.sign(string_to_sign).signature

    @classmethod
    def encrypt_file(self, plaintext_filename, key):
        '''
        Encrypts plaintext_filename to a temporary encrypted file, with the
        filename returned as encrypted_filename.

        Assumes files are already on filesystem (retrieved previously from server)

        Returns tuple of (encrypted_filename, checksum, encrypted_length).
        '''

        # check that plaintext_file is valid and we can read it
        if not os.path.isfile(plaintext_filename):
            raise IOError("File not found: {0}".format(plaintext_filename))
            # following will throw exception should permission be denied
        try:
            plaintext_file_handle = open(plaintext_filename, 'rb')
        except IOError:
            plaintext_file_handle.close()
            # create temporary file for encrypted data
        try:
            encrypted_file_handle = tempfile.NamedTemporaryFile(prefix="e2e", suffix=".bin",delete=False)
            encrypted_filename = encrypted_file_handle.name
        except IOError:
            encrypted_file_handle.close()

        # Create file header information and generate keys
        dk = nacl.bindings.crypto_secretstream_xchacha20poly1305_keygen()
        m = hashlib.md5()
        edkN = self.random_nonce()
        edk = self.encrypt_secret(key, dk, edkN)
        edk = edk[len(edkN):]
        encrypted_length = 0
        header = "{0}.{1}.{2}.".format(FILE_VERSION, BaseCrypto.base64encode(edk).decode("utf-8"), BaseCrypto.base64encode(edkN).decode("utf-8"))
        # last field is encrypted data

        header_bytes = BaseCrypto.to_bytes(header)
        m.update(header_bytes)
        encrypted_file_handle.write(header_bytes)
        encrypted_length += len(header_bytes)

        state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
        stream_header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, dk)

        encrypted_file_handle.write(stream_header)
        m.update(stream_header)
        encrypted_length += len(stream_header)

        done = False
        # simulate two element queue to detect EOF for TAG_FINAL
        next_block = None
        head_block = plaintext_file_handle.read(BLOCK_SIZE)
        while not done:
            next_block = plaintext_file_handle.read(BLOCK_SIZE)
            if next_block == b'':
                tag = TAG_FINAL
                # Next block is empty, so we know we hit EOF
                # block is full and we haven't hit EOF
                done = True
            else:
                tag = TAG_MESSAGE

            stream_bytes = nacl.bindings.crypto_secretstream_xchacha20poly1305_push(state, head_block, tag=tag)
            encrypted_file_handle.write(stream_bytes)
            m.update(stream_bytes)
            encrypted_length += len(stream_bytes)
            head_block = next_block

        # cleanup
        encrypted_file_handle.close()
        plaintext_file_handle.close()
        # Cannot import EncryptedFileInfo class here, so return an tuple that can
        # be used in the client.py file to construct the EncryptedFileInfo object
        # Returns encrypted_filename, md5 checksum, length in bytes of encrypted file
        return (encrypted_filename, base64.b64encode(m.digest()), encrypted_length)

    @classmethod
    def decrypt_file(self, encrypted_filename, destination_filename, key):
        '''
        Decrypts encrypted_filename, and outputs plaintext file in destination_filename.
        Assumes files are already on filesystem (retrieved previously from server).
        '''
        # Check if the file exists, and we can read it with proper permissions
        if not os.path.isfile(encrypted_filename):
            raise IOError("File not found: {0}".format(encrypted_filename))

        # We are going to use two file handles for the Encrypted File
        # Handle #1 is going to be used to read the header information
        # Handle #2 is going to skip the header information, and be used to
        # extract the ciphertext for decryption
        # This is necessary so we can efficiently extract the header without
        # reading too much of the file information to optimized disk IO

        # open file handle to encrypted_file
        try:
            encrypted_file_handle = open(encrypted_filename, 'rb')
        except IOError:
            encrypted_file_handle.close()

        # open file handle to encrypted_file header
        try:
            encrypted_file_header_handle = open(encrypted_filename, 'rb')
        except IOError:
            encrypted_file_header_handle.close()

        # Try to create destination plaintext_file
        try:
            destination_file_handle = open(destination_filename, 'wb+')
        except IOError:
            destination_file_handle.close()

        # Most modern Filesystems use a 4KB, or 4096 byte block size
        # When you read any information, the OS has to read the entire 4KB block
        # whether or not it is used. Since 4KB is already going to be read,
        # and we know the E3DB file header information is much less than 4KB,
        # this size of read makes sense to extract the header from the file
        h1 = encrypted_file_header_handle.read(4096)
        e3db_header_block = h1.split(b'.')

        # grab the version, edk, and edkN
        file_version = int(e3db_header_block[0])
        if file_version != FILE_VERSION:
            raise RuntimeError("File version: {0} does not match supported version: {1}".format(file_version, FILE_VERSION))
        edk = BaseCrypto.base64decode(e3db_header_block[1])
        edkN = BaseCrypto.base64decode(e3db_header_block[2])
        dk = self.decrypt_secret(key, edk, edkN)

        # Calculate length of the header so we know where to start reading
        # the ciphertext of the encrypted_file_handle. +3 accounts for the
        # 3 bytes used by the "." delimiters between fields
        e3db_header_length = len(e3db_header_block[0] + e3db_header_block[1] + e3db_header_block[2]) + 3
        encrypted_file_header_handle.close()

        # Open the encrypted_file_handle, starting at the first byte of the ciphertext
        # discard the first bytes of the header, since we already parsed them
        encrypted_file_handle.read(e3db_header_length)

        libsodium_header = encrypted_file_handle.read(nacl.bindings.crypto_secretstream_xchacha20poly1305_HEADERBYTES)

        # Setup libsodium stream cipher decryption
        state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
        nacl.bindings.crypto_secretstream_xchacha20poly1305_init_pull(state, libsodium_header, dk)

        while True:
            read_block = encrypted_file_handle.read(BLOCK_SIZE + ABYTES)
            message, tag = nacl.bindings.crypto_secretstream_xchacha20poly1305_pull(state, read_block)

            if tag == TAG_MESSAGE:
                # write decrypted block to file
                destination_file_handle.write(message)
            elif tag == TAG_FINAL:
                # write the final block
                destination_file_handle.write(message)
                break
            else:
                raise RuntimeError("Decryption failed, TAG_MESSAGE or TAG_FINAL not present for ciphertext block: {0} \n message: {1} \n tag: {2}".format(read_block, message, tag))

        encrypted_file_handle.close()
        destination_file_handle.close()

    @classmethod
    def verify(self, signature, message, public_key):
        """
        Validates the signature on a message.

        Parameters
        ----------
        signature : bytes
            Raw bytes of the signature for the message.
        
        message : bytes
            Raw bytes of the hashed message.
        
        public_key : bytes
            Raw bytes of the public signing key.

        Returns
        -------
        str
            If verify succeeds, the message is returned. Otherwise, an error occurs.
        """
        verify_key = nacl.signing.VerifyKey(public_key)
        return verify_key.verify(message, signature)

    @classmethod
    def decrypt_field(self, encrypted_field, ak):
        """
        Decrypt a field using Libsodium.

        Parameters
        ----------
        encrypted_field : str
            Encrypted string.
        
        ak : bytes
            Raw bytes of the access key to be used as the decryption key.

        Returns
        -------
        str
            Decrypted field as a UTF-8 string.
        """
        fields = encrypted_field.split(".")
        edk = self.base64decode(fields[0])
        edkN = self.base64decode(fields[1])
        ef = self.base64decode(fields[2])
        efN = self.base64decode(fields[3])
        dk = self.decrypt_secret(ak, edk, edkN)
        return self.decrypt_secret(dk, ef, efN).decode("utf-8")

    @classmethod
    def encrypt_field(self, field, access_key):
        """
        Encrypt a string into the standard Tozny quad format using Libsodium's secretbox.

        Parameters
        ----------
        field : string  
            The string of data to encrypt as a data field.
        access_key : bytes
            The access key bytes to encrypt the field with.
    
        Returns
        -------
        str
         The Tozny dotted quad encrypted field 
        """
        dk = self.random_key()
        efN = self.random_nonce()
        ef = self.encrypt_secret(dk, field, efN)
        edkN = self.random_nonce()
        edk = self.encrypt_secret(access_key, dk, edkN)
        encrypted_byte_strings = (edk.ciphertext, edk.nonce, ef.ciphertext, ef.nonce)
        encrypted_strings = map(lambda x: self.base64encode(x).decode('utf-8'), encrypted_byte_strings)
        return ".".join(encrypted_strings)
