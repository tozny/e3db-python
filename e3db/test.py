from sodium_crypto import *
key = SodiumCrypto.random_key()
encrypted_filename, md5, size = SodiumCrypto.encrypt_file("1gb.zero", key)

SodiumCrypto.decrypt_file(encrypted_filename, "plaintext.output.txt", key)
