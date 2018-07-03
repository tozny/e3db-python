import os
from config import Config
from client import Client
if 'FIPS_MODE' in os.environ and bool(os.environ['FIPS_MODE']):
    from nist_crypto import NistCrypto as Crypto
else:
    from sodium_crypto import SodiumCrypto as Crypto
from exceptions import APIError, QueryError, LookupError, ConflictError, CryptoError
