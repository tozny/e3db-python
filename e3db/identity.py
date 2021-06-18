from e3db.types.signing_key_pair import SigningKeyPair
from e3db.types.encyption_key_pair import EncryptionKeyPair
import os
from e3db import Client
if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
    from .nist_crypto import NistCrypto as Crypto
else:
    from .sodium_crypto import SodiumCrypto as Crypto


class Identity:
    """This is a placeholder class pending further development of Identity Login"""


    @staticmethod
    def derive_note_creds(user_name: str, password: str, realm_name: str):
        """
        Derive the note name, crypto, and signing keys for an note containing identity credentials.

        Parameters
        ----------
        user_name : string
            username The username credentials are being derived for.
        
        password : string
           password The secret password for the user.

        realm_name : string
             realmName The identity realm name.
        
        NOTE: Only password based cred_type is supported at this time

        Returns
        -------
        Tuple[string, EncryptionKeyPair, SigningKeyPair]
            Where the base 64 encoded string is the hash of the user name and the realm name
        """
        
        name_seed = f"{user_name.lower()}@realm:{realm_name}"
        note_name_as_bytes = Crypto.hashString(name_seed)
        note_name_as_b64_string = Crypto.base64encode(note_name_as_bytes).decode('utf-8')
        password_bytes = Crypto.to_bytes(password)
        name_seed_bytes = Crypto.to_bytes(name_seed)
        key_pair = Crypto.derive_crypto_keypair(password_bytes, name_seed_bytes)

        salt_in_bytes = Crypto.to_bytes(key_pair.public_key + key_pair.private_key) 
        signing_key_pair = Crypto.derive_signing_keypair(password_bytes, salt_in_bytes)

        return note_name_as_b64_string, key_pair, signing_key_pair
