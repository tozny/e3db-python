import e3db
import os
import binascii

# A registration token is required to set up a client. In this situation,
# we assume an environment variable called REGISTRATION_TOKEN is set
token = os.environ["REGISTRATION_TOKEN"]

print "Using Registration Token: {0}".format(token)

public_key, private_key = e3db.Client.generate_keypair()

print "Public Key: {0}".format(public_key)
print "Private Key: {0}".format(private_key)

wrapped_key = e3db.PublicKey('curve25519', public_key)

# Clients must be registered with a name unique to your account to help
# differentiate between different sets of credentials in the Admin Console.
# In this example, the name is set at random
client_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))

print "Client Name: {0}".format(client_name)

client_info = e3db.Client.register(token, client_name, wrapped_key, api_url="https://dev.e3db.com")

print "Client ID: {0}".format(client_info['client_id'])
print "API Key ID: {0}".format(client_info['api_key_id'])
print "API Secret: {0}".format(client_info['api_secret'])

config = e3db.Config('1',
    client_info['client_id'], \
    client_info['api_key_id'], \
    client_info['api_secret'], \
    '', \
    public_key, \
    private_key, \
    )

client = e3db.Client(config())

client.debug()
