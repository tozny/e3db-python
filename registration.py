import e3db
import os

# A registration token is required to set up a client. In this situation,
# we assume an environment variable called REGISTRATION_TOKEN is set
token = os.environ["REGISTRATION_TOKEN"]

print "Using Registration Token: {0}".format(token)

public_key, private_key = e3db.Client.generate_keypair()

print "Public Key: {0}".format(public_key)
print "Private Key: {0}".format(private_key)
