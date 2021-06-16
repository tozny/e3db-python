from e3db.base_crypto import BaseCrypto 
from e3db.sodium_crypto import SodiumCrypto

# Credentials
CREDS = {
    "private_signing_key": "d55u6bLR9tkMVA4OwYIPepOOeXVSHHEit8VoXGRMQiaf5wKRk9gooP9pN3LBJ28BIW9fZ9-ZZPLVsHtuPqkRSQ",
    "public_signing_key": "n-cCkZPYKKD_aTdywSdvASFvX2ffmWTy1bB7bj6pEUk",
	"private_key": "hZ-7-YM149qi2OXxdmFyUPKuLIItmmwSuvk5ZJ64JKo",
	"api_secret": "87accc0775dd5613574e4b67e85a6b4505d4ceeb879e573f4561c79adaeeebc1",
	"client_id": "0e8eb8c6-839f-46ca-9843-801c539e490f",
	"public_key": "zi2mH1QqnX9ZlUQBPcK1a4QLbwx4iTY21u5olrx5jns",
	"version": "2",
	"api_key_id": "081a1b3905485fcb6581be11e2c174bf2185e8326d139354bb68a77c2b591c6",
	"api_url": "\"http://platform.local.tozny.com:8000",
	"client_email": ""
}
PUBLIC_SIGNING_KEY       = CREDS["public_signing_key"]
CLIENT_ID                = CREDS["client_id"]

# String to sign 
SECRET_KEY_BYTES         = 32
HASHING_ALGORITHM        = "BLAKE2B"
SIGNATURE_TYPE           = "ED25519"
AUTHENTICATION_METHOD    = "TSV1-" + SIGNATURE_TYPE + "-" + HASHING_ALGORITHM 
TIMESTAMP                = "1000000000" 
CALL_METHOD              = "POST" 
CALL_PATH                = "/x/y%2Fz"
QUERY_STRING             = "bar=baz&foo=quux"
NONCE                    = "59a7d5b6-35d2-41fd-99b2-066a07bd1632"
HEADER_STRING            = f"{AUTHENTICATION_METHOD}; {PUBLIC_SIGNING_KEY}; {TIMESTAMP}; {NONCE}; uid:{CLIENT_ID}"

# Known hash and signature
KNOWN_HASH      = "8e480794b093521ce2a1fa7e6f7afa394ff38b23869389f3165cdb15bfebfdc7"
KNOWN_SIGNATURE = "Gz2ONHJF6kcUX-2yZdveMuSShDf709wciDhbifNBQeAaGqqMW7B6DbQYlZ7KykvIX1DHZ7tolTH6u-gXq_n5CQ"

def test_public_signing_key_derivation():
    """
    Asserts that deriving the public signing key from the PyNacl SigningKey 
    is equivalent to the known public signing key. 
    """
    private_b64_decoded = BaseCrypto.base64decode(CREDS["private_signing_key"])
    signing_key = SodiumCrypto.generate_signing_key(private_b64_decoded[:SECRET_KEY_BYTES])
    derived_public_signing_key = signing_key.verify_key
    public_signing_key_encoded = BaseCrypto.base64encode(derived_public_signing_key).decode("utf-8")
    assert(public_signing_key_encoded == CREDS["public_signing_key"])

def test_private_signing_key_derivation():
    """
    Asserts that deriving the private signing key from the PyNacl SigningKey
    is equivalent to the known private signing key. 
    """
    private_b64_decoded = BaseCrypto.base64decode(CREDS["private_signing_key"])
    signing_key = SodiumCrypto.generate_signing_key(private_b64_decoded[:SECRET_KEY_BYTES])
    derived_private_signing_key = signing_key._signing_key
    private_signing_key_encoded = BaseCrypto.base64encode(derived_private_signing_key).decode("utf-8")
    assert(private_signing_key_encoded == CREDS["private_signing_key"])

def test_blake2b_hash():
    """
    Asserts that the Blake2B hash of the string to sign is equivalent to the
    known hash value of the string to sign. 
    """
    string_to_hash =  f"{CALL_PATH}; {QUERY_STRING}; {CALL_METHOD}; {HEADER_STRING}"
    hash_to_sign = BaseCrypto.hashString(string_to_hash).hex()
    assert(hash_to_sign == KNOWN_HASH)

def test_signature():
    """
    Asserts that the generated Ed25519 signature is equivalent to the known signature value. 
    """
    string_to_hash =  f"{CALL_PATH}; {QUERY_STRING}; {CALL_METHOD}; {HEADER_STRING}"
    string_to_sign = BaseCrypto.hashString(string_to_hash)
    private_b64_decoded = BaseCrypto.base64decode(CREDS["private_signing_key"])[:SECRET_KEY_BYTES]
    full_signature = SodiumCrypto.sign_string(string_to_sign, private_b64_decoded)
    signature_64 = BaseCrypto.base64encode(full_signature).decode("utf-8")
    assert(signature_64 == KNOWN_SIGNATURE)
