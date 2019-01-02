# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------
import e3db

# Configuration files live in ~/.tozny and you can have several
# different "profiles" like *dev* and *production*.

# Load ~/.tozny/dev/e3db.json profile
# conf = e3db.Config.load('dev')

# Load default config in ~/.tozny/e3db.json
conf = e3db.Config.load()

# Now create a client using that configuration.
client = e3db.Client(conf)

record_type = "test_large_files"

# Plaintext file that we want to encrypt and send to E3DB for storage
plaintext_filename = "mylargefile.txt"

# Encrypt and write the file to the E3DB Server
encrypted_file_meta = client.write_file(record_type, plaintext_filename)

# Sharing, Authorizer role, etc all works the same with large files as it does
# with normal records. In this example we are sharing the file with another client
isaac_client_id = 'db1744b9-3fb6-4458-a291-0bc677dba08b'
client.share(record_type, isaac_client_id)

# Now we can read the file from the E3DB server
# The File will be decrypted and then written to disk as "decrypted-mylargefile.txt"
decrypted_plaintext_filename = "decrypted-mylargefile.txt"
read_file_info = client.read_file(encrypted_file_meta.record_id, decrypted_plaintext_filename)

# Now you can do normal File operations, such as reading the decrypted file contents
with open(decrypted_plaintext_filename, 'r') as f:
    print(f.read())
