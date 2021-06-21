import uuid
import requests
from requests.auth import AuthBase
from .sodium_crypto import SodiumCrypto
from .base_crypto import BaseCrypto
import time
from urllib.parse import urlparse, parse_qsl, urlencode

class E3DBTSV1Auth(AuthBase):
    HASHING_ALGORITHM = "BLAKE2B"
    SIGNATURE_TYPE = "ED25519"
    AUTHENTICATION_METHOD = "TSV1-" + SIGNATURE_TYPE + "-" + HASHING_ALGORITHM
    AUTHORIZATION_HEADER = "Authorization"
    SECRET_KEY_BYTES = 32

    def __init__(self, private_signing_key: str, client_id: str):
        self.private_signing_key = private_signing_key
        self.client_id = client_id

        self.private_b64_decoded = BaseCrypto.base64decode(self.private_signing_key)[:self.SECRET_KEY_BYTES]
        self.signing_key = SodiumCrypto.generate_signing_key(self.private_b64_decoded)
        self.public_signing_key = self.signing_key.verify_key

        self.public_b64 = BaseCrypto.base64encode(self.public_signing_key).decode("utf-8")

    def __call__(self, r: requests.PreparedRequest):
        """
        TSV1 authentication of requests. Sets the authorization header of a request
        to be the client's signature. 

        Signature is generated by deriving and decoding signing key, calculating
        the header values from the request, and then signing the hash of the header values
        wth the client's private signing key.

        Parameters
        ----------
        r : requests.Request

        Returns
        -------
        requests.Request
            Request with authentication headers set with signature. 
        """
        if self.public_signing_key == "":
            raise RuntimeError("Cannot make a tsv1 request without a signing key.")
        timestamp = int(time.time())
        nonce = str(uuid.uuid4())
        self.create_tsv1_signature(r, self.public_b64, self.private_b64_decoded, self.client_id, nonce, timestamp)
        return r

    @classmethod
    def create_tsv1_signature(self, r: requests.models.PreparedRequest, public_b64: str, private_b64_decoded: bytes, client_id: str, nonce: str, timestamp: int):
        """
        Creates a TSV1 Signature and sets the request's authorization header.

        Parameters
        ----------
        r : requests.Request
        
        nonce : UUID

        timestamp : int

        Returns
        -------
        None
        """

        # Generate header values
        header_string = f"{self.AUTHENTICATION_METHOD}; {public_b64}; {timestamp}; {nonce}; uid:{client_id}"
        
        # Parse and sort query parameters
        url_components = urlparse(r.url)
        query_components = parse_qsl(url_components.query, keep_blank_values=True)
        query_components.sort()
        query_string = urlencode(query_components)

        call_path = url_components.path

        call_method = r.method

        # Hash header values
        string_to_hash = f"{call_path}; {query_string}; {call_method}; {header_string}"

        # Sign hash
        string_to_sign = BaseCrypto.hashString(string_to_hash)
        full_signature = SodiumCrypto.sign_string(string_to_sign, private_b64_decoded)
        signature_b64 = BaseCrypto.base64encode(full_signature).decode("utf-8")

        # Add authorization headers to request
        auth_header = f"{header_string}; {signature_b64}"
        r.headers[self.AUTHORIZATION_HEADER] = auth_header
