from e3db.types.signing_key_pair import SigningKeyPair
from e3db.types.encyption_key_pair import EncryptionKeyPair
from e3db.identity import Identity

def test_derive_note_creds():
    """Assert that note name, encryption and signing keys all match values generated in js-sdk"""
    target_note_name = "h7ybsbRZfkmvt8Xib2I9RbOLOX1igfHHgey7rH_SZRM"
    target_pk = 'Ei8BaVIoaEXSJ_LCfWyDquEUYzGzFLDh1dSnVLEYRTE'
    target_sk = 'UE4LcHTiGySNgvRkfftLyBCEepMJpLAA1XsBz1g4yGw'
    target_psk = 'SFIFdByyg7T-YVnZ2I7k1hOhA5ZZhOLSdjlkxA0xzA0'
    target_ssk = 'TAUD9JVnwTu5r9_bCWPw0h8Fa3_k6tqlodfeS1QI-VVIUgV0HLKDtP5hWdnYjuTWE6EDllmE4tJ2OWTEDTHMDQ'

    user_name = "FRED"
    realm_name = "IntegrationTest"
    password = "correcthorsebatterystaple"
    hashed_name, key_pair, signing_pair = Identity.derive_note_creds(user_name, password, realm_name)

    assert(type(hashed_name) == str)
    assert(type(key_pair) == EncryptionKeyPair)
    assert(type(signing_pair) == SigningKeyPair)
    assert(hashed_name == target_note_name)
    assert(target_sk == key_pair.private_key)
    assert(target_pk == key_pair.public_key)
    assert(target_ssk == signing_pair.private_key)
    assert(target_psk == signing_pair.public_key)
