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
    pubkey, privkey = e3db.Crypto.generate_keypair()
    assert(type(privkey) == nacl.public.PrivateKey)
    assert(type(pubkey) == nacl.public.PublicKey)

def test_public_key_encoding():
    pubkey = 'RMG04iil2HDaUWye9wMVG8RmIL_s5tPOilRoiLUjLT8'
    decoded = e3db.Crypto.decode_public_key(pubkey)
    encoded = e3db.Crypto.encode_public_key(decoded)
    assert(pubkey == encoded)
    assert(type(decoded) == nacl.public.PublicKey)

def test_private_key_encoding():
    privkey = '_wSGC32a3g_VOPPy3kILDqzKLa1tPwdTNW3DQrJMPxk'
    decoded = e3db.Crypto.decode_private_key(privkey)
    encoded = e3db.Crypto.encode_private_key(decoded)
    assert(privkey == encoded)
    assert(type(decoded) == nacl.public.PrivateKey)
