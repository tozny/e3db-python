import base64
import nacl.utils
import nacl.secret
import nacl.public

class Crypto:
    @classmethod
    def decode_public_key(key):
        return nacl.public.PublicKey(Crypto.base64decode(key))

    @classmethod
    def encode_public_key(self, key):
        return Crypto.base64encode(str(key))

    @classmethod
    def decode_private_key(key):
        return nacl.public.PrivateKey(Crypto.base64decode(key))

    @classmethod
    def encode_private_key(self, key):
        return Crypto.base64encode(str(key))

    @classmethod
    def secret_box_random_key():
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    @classmethod
    def secret_box_random_nonce():
        return nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    @classmethod
    def base64decode(s):
        # From https://stackoverflow.com/a/9956217
        # Python base64 implementation requires padding, which may not be present in the
        # encoded public/private keypair
        return base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))

    @classmethod
    def base64encode(self, s):
        # remove "=" padding for general SDK compatibility
        return base64.urlsafe_b64encode(s).strip("=")

    @classmethod
    def generate_keypair(self):
        # return public, private
        key = nacl.public.PrivateKey.generate()
        return key, key.public_key
