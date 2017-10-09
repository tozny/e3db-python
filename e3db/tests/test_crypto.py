import e3db
import nacl.utils
import nacl.secret
import nacl.public

def test_base64():
    # ensure encoding and decoding string results in same string as original
    string = "testing base64 is the best! #testing"
    encoded = e3db.Crypto.base64encode(string)
    decoded = e3db.Crypto.base64decode(encoded)
    assert(string == decoded)

def test_generate_keypair():
    privkey, pubkey = e3db.Crypto.generate_keypair()
    assert(type(privkey) == nacl.public.PrivateKey)
    assert(type(pubkey) == nacl.public.PublicKey)
