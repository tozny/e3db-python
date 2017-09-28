import base64
import nacl.public
import nacl.utils
import nacl.secret

class Crypto:
    def __init__(self):
        pass
    def decode_public_key(key):
        return nacl.public.PublicKey(self.base64decode(key))
    def encode_public_key(key):
        return self.base64encode(str(key))
    def decode_private_key(key):
        return nacl.public.PrivateKey(self.base64decode(key))
    def encode_private_key(key):
        return self.base64encode(str(key))
    def secret_box_random_key():
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    def secret_box_random_nonce():
        return nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    def base64decode(self, s):
        # From https://stackoverflow.com/a/9956217
        # Python base64 implementation requires padding, which may not be present in the
        # encoded public/private keypair
        return base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))
    def base64encode(self, s):
        # remove "=" padding for general SDK compatibility
        return base64.urlsafe_b64encode(s).strip("=")
