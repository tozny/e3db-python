# This program provides a simple example illustrating how to programmatically
# register a client with InnoVault and e3db. In some situations, it's preferable
# to register a client from the server or system that will be using its
# credentials (to ensure that all data is truly encrypted from end-to-end
# with no possibilities of a credential leak). For more detailed information,
# please see the documentation home page: https://tozny.com/documentation/e3db
#
# Copyright:: Copyright (c) 2017 Tozny, LLC
# License::   Public Domain

# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------

import e3db

# required to generate random client id
import os
import binascii

# A registration token is required to set up a client. In this situation,
# we assume an environment variable called REGISTRATION_TOKEN is set
token = os.environ["REGISTRATION_TOKEN"]
api_url = os.environ["DEFAULT_API_URL"] # TODO REMOVE

print "Using Registration Token: {0}".format(token)

public_key, private_key = e3db.Client.generate_keypair()

print "Public Key: {0}".format(public_key)
print "Private Key: {0}".format(private_key)

# Clients must be registered with a name unique to your account to help
# differentiate between different sets of credentials in the Admin Console.
# In this example, the name is set at random
client_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))

print "Client Name: {0}".format(client_name)

# Passing all of the data above into the registration routine will create
# a new client with the system. Remember to keep your private key private!
#client_info = e3db.Client.register(token, client_name, public_key, api_url=api_url) # TODO remove api_url

# Optionally, you can automatically back up the credentials of the newly-created
# client to your InnoVault account (accessible via https://console.tozny.com) by
# passing your private key and a backup flag when registering. The private key is
# not sent anywhere, but is used by the newly-created client to sign an encrypted
# copy of its credentials that is itself stored in e3db for later use.
#
# Client credentials are not backed up by default.

client_info = e3db.Client.register(token, client_name, public_key, private_key=private_key, backup=True, api_url=api_url)

api_key_id, api_secret = client_info.get_api_credentials()
client_id = client_info.get_client_id()

print "Client ID: {0}".format(client_id)
print "API Key ID: {0}".format(api_key_id)
print "API Secret: {0}".format(api_secret)

# ---------------------------------------------------------
# Usage
# ---------------------------------------------------------

# Once the client is registered, you can use it immediately to create the
# configuration used to instantiate a Client that can communicate with
# e3db directly.

config = e3db.Config(
    client_id, \
    api_key_id, \
    api_secret, \
    public_key, \
    private_key, \
    api_url=api_url \
    )

# Now create a client using that configuration.
client = e3db.Client(config())

# From this point on, the new client can be used as any other client to read
# write, delete, and query for records. See the `simple.py` documentation
# for more complete examples ...
