import nacl.utils
import nacl.public
import nacl.public
import e3db

# based on https://pynacl.readthedocs.io/en/latest/public/, but with e3db wrappers

# create bob keys
pkbob, skbob = e3db.Crypto.generate_keypair()

skbob_encoded = e3db.Crypto.encode_private_key(skbob)
skbob_decoded = e3db.Crypto.decode_private_key(skbob_encoded)

pkbob_encoded = e3db.Crypto.encode_public_key(pkbob)
pkbob_decoded = e3db.Crypto.decode_public_key(pkbob_encoded)


# create alice keys
pkalice, skalice = e3db.Crypto.generate_keypair()

skalice_encoded = e3db.Crypto.encode_private_key(skalice)
skalice_decoded = e3db.Crypto.decode_private_key(skalice_encoded)

pkalice_encoded = e3db.Crypto.encode_public_key(pkalice)
pkalice_decoded = e3db.Crypto.decode_public_key(pkalice_encoded)

bob_box = e3db.Crypto.box(skbob_decoded, pkalice_decoded)

message = "Tozny is awesome."

nonce = e3db.Crypto.secret_box_random_nonce()

encrypted = bob_box.encrypt(message, nonce)

alice_box = e3db.Crypto.box(skalice_decoded, pkbob_decoded)

plaintext = alice_box.decrypt(encrypted)

assert(message == plaintext)
