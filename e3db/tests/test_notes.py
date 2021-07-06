from e3db.types.signing_key_pair import SigningKeyPair
from e3db.types.encyption_key_pair import EncryptionKeyPair
from e3db import sodium_crypto
from e3db.exceptions import NoteValidationError, ConflictError, APIError
import e3db
from e3db.types import Note, NoteKeys, NoteOptions
import pytest
from uuid import uuid4
import binascii
import os


token = os.environ["REGISTRATION_TOKEN"]
api_url = os.environ["DEFAULT_API_URL"]

# these are placeholder values for testing & can be removed on ReadNote is functional.
public_key = '88ph_j2dytMVTBsgCm-9hU608WyJgpB51BuWDQa9AGI'
private_key = 'iCiUo33otFUyyMp_XQZvdSG4S51HG8gypBEhRI_E3W8'
writer_public_signing_key = 'Yn-I-ceRTjVpoJOSOrJvc03R9xT4YV7Sptxo-eQYN5w'
reader_public_signing_key = 'MpSWcRYZqLRzIaxl6sYno7WPy0O6t2vjttkoj_pn_5Y'
writer_public_key = 'c7F5iyzDblgJEIR4Ks7r32YuqOZXD2fW_hPvBCzVEgU'

note_options = NoteOptions(
  note_writer_client_id='57b30f55-fcde-4cf6-99ac-2687610d8add',
  max_views=-1,
  id_string='globalNoteName-c5f281bf-65df-4af2-99e9-97fdc890b631',
  expiration='0001-01-01T00:00:00Z',
  expires=False,
  type='',
  plain={},
  file_meta={}
)

note_keys = NoteKeys(
  mode='Sodium',
  note_recipient_signing_key=reader_public_signing_key,
  note_writer_signing_key=writer_public_signing_key,
  note_writer_encryption_key=writer_public_key,
  encrypted_access_key='Dmf1mPsezH0t6BRBinn4HT5vv6YqvFuB9izOXpp_jmTzkqMojEue5yRi1fHLJyBD._ah4FepASuU0Yh76ZUG3cRbphZXdO5t7',
)

data = {
  'secret': 'qD3qRA3Pte8v6iJAeP18IqwdqR9p4PepqYiglhbltS5KxpFVqR2GCZLxsy563Xqc.DFLYPXYRIRXoRw4UnKgn_J5QeY8Wq8J5.v8frFE7NTvrb9yR0VYDoVAkUI2BzdrFzGXV114J4QaMGMIUQJY6kJod-b7Hf3A_mP-qGWdM5Jx6u0v9d8jpvsTx9NMchErz82Pa4xdL9-MkGUODCVbXawOKg1dQ_xzM-5ywB2Mcn8ozw0jQwXlxBjZNGch2ms5216OuT4M9gUhBobz4ZnW-Ul6Dh39dXFwqPx5w8-FHKIENzR80rnP00pK4muJHImqmO1-EusQGqbQVbSGTrpvOp.btq9Aw0dsr-J_0o5e0oLJb3D6mRGAo4S'
}

signature = 'e7737e7c-1637-511e-8bab-93c4f3e26fd9;356ba56c-0932-4e44-865d-d9a4ac6d33cb;86;jAdtUnN0w7Eomn3_Cq7Xe0sM34b2FYJ-uIxtqNuygmT9-5nYqK8Lm59zZABIS3eUF2igdKANiCkdHIiLaXQUAwc720777d-fe43-4ded-bf90-90d2726f113e'

encrypted_note = Note(
  data,
  note_keys,
  note_options
)


# Encrypt a Note: Needs writer key pair, writer signing key pair, and unencoded options
writer_public_key_A, writer_private_key_A = e3db.Client.generate_keypair()
writer_key_pair_A = EncryptionKeyPair(writer_public_key_A, writer_private_key_A)
writer_public_signing_key_A, writer_private_signing_key_A = e3db.Client.generate_signing_keypair()
writer_signing_key_pair_A = SigningKeyPair(writer_public_signing_key_A, writer_private_signing_key_A)
reader_public_key_A, reader_private_key_A = e3db.Client.generate_keypair()
reader_public_signing_key_A, reader_private_signing_key_A = e3db.Client.generate_signing_keypair()
unencrypted_data_A = {
  'secret': 'data' 
}

def generate_note_options(client_id: str) -> NoteOptions:
  return NoteOptions(
      note_writer_client_id=client_id,
      max_views=3,
      id_string=f"globalNoteName-${uuid4()}",
      expiration='0001-01-01T00:00:00Z',
      expires=False,
      type='',
      plain={},
      file_meta={}
    )


class TestNoteSupport():

  @classmethod
  def setup_class(self):
    """This code runs before the tests and assigns a dynamically configured client"""
    client1_public_key, client1_private_key = e3db.Client.generate_keypair()
    client1_public_signing_key, client1_private_signing_key = e3db.Client.generate_signing_keypair()
    client1_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
    test_client1 = e3db.Client.register(token, client1_name, client1_public_key, backup=False, api_url=api_url, 
                                        public_signing_key=client1_public_signing_key,
                                        private_signing_key=client1_private_signing_key)
    client1_api_key_id = test_client1.api_key_id
    client1_api_secret = test_client1.api_secret
    client1_id = test_client1.client_id

    client1_config = e3db.Config(
        client1_id,
        client1_api_key_id,
        client1_api_secret,
        client1_public_key,
        client1_private_key,
        api_url=api_url,
        public_signing_key=client1_public_signing_key,
        private_signing_key=client1_private_signing_key
    )

    self.client1 = e3db.Client(client1_config())

    # Client 2
    client2_public_key, client2_private_key = e3db.Client.generate_keypair()
    client2_public_signing_key, client2_private_signing_key = e3db.Client.generate_signing_keypair()
    client2_name = "client_{0}".format(binascii.hexlify(os.urandom(16)))
    test_client2 = e3db.Client.register(token, client2_name, client2_public_key, backup=False, api_url=api_url, 
                                        public_signing_key=client2_public_signing_key,
                                        private_signing_key=client2_private_signing_key)
    client2_api_key_id = test_client2.api_key_id
    client2_api_secret = test_client2.api_secret
    client2_id = test_client2.client_id

    client2_config = e3db.Config(
        client2_id,
        client2_api_key_id,
        client2_api_secret,
        client2_public_key,
        client2_private_key,
        api_url=api_url,
        public_signing_key=client2_public_signing_key,
        private_signing_key=client2_private_signing_key
    )

    self.client2 = e3db.Client(client2_config())

  def test_decrypt_valid_note_succeeds(self):
    '''
    Asserts that a note with the correct decrypted data is returned.
    '''
    encrypted_note.signature = signature
    decrypted_note = e3db.Client.decrypt_note(encrypted_note, private_key)
    assert(decrypted_note.data['secret'] == 'data')

  def test_decrypt_note_without_signature_fails_by_default(self):
    '''
    Asserts that decryption of a note without a signature fails.
    '''
    encrypted_note.signature = ''
    with pytest.raises(NoteValidationError):
      e3db.Client.decrypt_note(encrypted_note, private_key)

  def test_decrypt_note_without_signature_not_error_if_verify_signature_set_to_false(self):
    '''
    Asserts that decryption fo a not without a signature will not fail if
    the boolean flag verify_signature is set to False
    '''
    encrypted_note.signature = ''
    decrypted_note = e3db.Client.decrypt_note(encrypted_note, private_key, verify_signature=False)
    assert(decrypted_note.data['secret'] == 'data')

  def test_decrypt_note_invalid_signing_key_fails(self):
    '''Asserts that decryption fails when the wrong private key is provided'''
    
    encrypted_note.signature = signature
    with pytest.raises(Exception):
      e3db.Client.decrypt_note(encrypted_note, public_key)

  def test_eak_encrypt_and_decrypt(self):
    """Asserts that an access key can be encrypted and decrypted"""     
    ak = sodium_crypto.SodiumCrypto.random_key()
    eak = sodium_crypto.SodiumCrypto.encrypt_note_ak(writer_private_key_A, reader_public_key_A, ak)
    decrypted_ak = sodium_crypto.SodiumCrypto.decrypt_note_eak(reader_private_key_A, eak, writer_public_key_A)
    assert(ak == decrypted_ak)

  def test_sign_field(self):
    field_key = 'signature'
    dummy_value = 'abc1234'
    pub_signing_key, priv_signing_key = e3db.Client.generate_signing_keypair()
    a_signed_dummy = sodium_crypto.SodiumCrypto.sign_field(field_key, dummy_value, priv_signing_key)
    verified_value = e3db.Client.verify_field(field_key, a_signed_dummy, pub_signing_key) 
    assert(dummy_value == verified_value)

  def test_encrypt_field(self):
    field_value = 'secret'
    access_key = sodium_crypto.SodiumCrypto.random_key()
    encrypted_field = sodium_crypto.SodiumCrypto.encrypt_field(field_value, access_key)
    decrypted_field = sodium_crypto.SodiumCrypto.decrypt_field(encrypted_field, access_key)
    assert(field_value == decrypted_field)
    

  def test_encrypt_valid_note_suceeds(self):
    '''Asserts that a note with the correct encrypted data is returned'''
    
    note_options_A = generate_note_options(self.client1.client_id)

    # NOTE: KEYS ARE BASE64URLENCODED string of bytes
    encrypted_note_A = e3db.Client.create_encrypted_note(unencrypted_data_A, 
                             reader_public_key_A,
                             reader_public_signing_key_A, 
                             writer_key_pair_A,
                             writer_signing_key_pair_A,
                             note_options_A)

    decrypted_note_A = e3db.Client.decrypt_note(encrypted_note_A, reader_private_key_A)
    assert(decrypted_note_A.data == unencrypted_data_A)
    
  def test_write_note(self):
    """Asserts that the write note method returns a note with a signature, a note_id and unencrypted data"""

    note_options = generate_note_options(self.client1.client_id)
    
    data1 = {
      "data" : "WRITE NOTE TEST"
    }
    # Write note from client1 to client1
    returned_note = self.client1.write_note(data1, 
                                self.client1.encryption_keys.public_key, 
                                              self.client1.signing_keys.public_key,
                                              note_options)
    assert(type(returned_note) == Note)
    assert(returned_note.note_id) is not None
    assert(returned_note.signature) is not None
    # Assert the data is returned unencrypted
    assert(returned_note.data == data1)

  def test_write_and_read_a_note_one_client(self):
    """Asserts that writing and reading a note returns the original data"""

    note_options2 = generate_note_options(self.client1.client_id)

    data2 = {
      "data" : str(uuid4())
    }
    # Write note from client1 to client1
    returned_note = self.client1.write_note(data2, 
                                            self.client1.encryption_keys.public_key, 
                                            self.client1.signing_keys.public_key,
                                            note_options2)
    assert(returned_note.note_id) is not None
    # Read the note from the server
    read_note = self.client1.read_note(note_id=returned_note.note_id)
    assert(read_note.note_id) is not None
    assert(read_note.note_id == returned_note.note_id)
    assert(read_note.data == data2)
    
  def test_write_and_read_a_note_two_clients(self):
    """Asserts that writing and reading a note returns the original data"""

    note_options2 = generate_note_options(self.client1.client_id)

    data = {
      "data" : str(uuid4())
    }
    # Write note from client1 to client2
    returned_note = self.client1.write_note(data, 
                                              self.client2.encryption_keys.public_key, 
                                              self.client2.signing_keys.public_key,
                                              note_options2)
    assert(returned_note.note_id) is not None
    # Read the note from the server
    read_note = self.client2.read_note(note_id=returned_note.note_id)
    assert(read_note.note_id) is not None
    assert(read_note.note_id == returned_note.note_id)
    assert(read_note.data == data)

  def test_write_and_read_a_note_by_name(self):
    """Asserts that writing and reading a note returns the original data"""

    note_options = generate_note_options(self.client1.client_id)

    data = {
      "data" : str(uuid4())
    }
    # Write note from client1 to client2
    returned_note = self.client1.write_note(data, 
                                              self.client2.encryption_keys.public_key, 
                                              self.client2.signing_keys.public_key,
                                              note_options)
    assert(returned_note.note_id) is not None
    # Read the note from the server using name
    read_note = self.client2.read_note_by_name(name=note_options.id_string)
    assert(read_note.note_id) is not None
    assert(read_note.note_id == returned_note.note_id)
    assert(read_note.data == data)

  def test_read_a_note_anonymously_by_id(self):
    """Asserts that writing and reading a note returns the original data"""

    note_options2 = generate_note_options(self.client1.client_id)

    data = {
      "data" : str(uuid4())
    }
    # Write note from client1 to client2
    returned_note = self.client1.write_note(data, 
                                              self.client2.encryption_keys.public_key, 
                                              self.client2.signing_keys.public_key,
                                              note_options2)
    assert(returned_note.note_id) is not None

    # Read the note from the server without a client - using the note ID - no client ID
    read_note = e3db.Client.read_anonymous_note_by_id(returned_note.note_id,
                                            self.client2.encryption_keys.private_key,
                                            self.client2.signing_keys.private_key,
                                            api_url=api_url)

    assert(read_note.note_id) is not None
    assert(read_note.note_id == returned_note.note_id)
    assert(read_note.data == data)

  def test_read_a_note_anonymously_by_name(self):
    """Asserts that writing and reading a note returns the original data"""

    note_options = generate_note_options(self.client1.client_id)

    data = {
      "data" : str(uuid4())
    }
    # Write note from client1 to client2
    returned_note = self.client1.write_note(data, 
                                              self.client2.encryption_keys.public_key, 
                                              self.client2.signing_keys.public_key,
                                              note_options)
    assert(returned_note.note_id) is not None

    # note_name is confusingly called id_string in the note options class.  
    note_name = note_options.id_string
    # Read the note from the server without a client - using the note ID - no client ID
    read_note = e3db.Client.read_anonymous_note_by_name(note_name,
                                            self.client2.encryption_keys.private_key,
                                            self.client2.signing_keys.private_key,
                                            api_url=api_url)

    assert(read_note.note_id) is not None
    assert(read_note.note_id == returned_note.note_id)
    assert(read_note.data == data)

  def test_write_anonymous_note(self):
    """Asserts we can write a note anonymously and without an instatiated client"""
    
    # No client ID in Note Options
    note_options = generate_note_options("")
    
    data = { "test data" : str(uuid4) }

    returned_note = e3db.Client.write_anonymous_note(data,
                                                self.client2.encryption_keys.public_key,
                                                self.client2.signing_keys.public_key,
                                                self.client1.encryption_keys,
                                                self.client1.signing_keys,
                                                note_options,
                                                api_url)
    assert(type(returned_note) == Note)
    assert(returned_note.note_id) is not None
    assert(returned_note.signature) is not None
    # Assert the data is returned unencrypted
    assert(returned_note.data == data)

# TODO: Test error response if no note exists by name or by ID (404)
  def test_read_note_returns_404_if_note_not_found(self):
    """Asserts 404 response when note does not exist"""
    note_options = generate_note_options(self.client1.client_id)

    data = {
      "data" : str(uuid4())
    }

    with pytest.raises(APIError) as excinfo:
      e3db.Client.read_anonymous_note_by_name(note_options.id_string,
                                            self.client2.encryption_keys.private_key,
                                            self.client2.signing_keys.private_key,
                                            api_url=api_url)
    assert("HTTP 404" in str(excinfo.value))


# TODO: Test name collision (409)
  def test_write_two_notes_with_same_name_returns_409(self):
    """Asserts naming collision results in 409"""
    note_options = generate_note_options(self.client1.client_id)

    returned_note = e3db.Client.write_anonymous_note(data,
                                                  self.client2.encryption_keys.public_key,
                                                  self.client2.signing_keys.public_key,
                                                  self.client1.encryption_keys,
                                                  self.client1.signing_keys,
                                                  note_options,
                                                  api_url)
    assert(type(returned_note) == Note)
    assert(returned_note.note_id) is not None
    with pytest.raises(ConflictError) as excinfo:
      e3db.Client.write_anonymous_note(data,
                                        self.client2.encryption_keys.public_key,
                                        self.client2.signing_keys.public_key,
                                        self.client1.encryption_keys,
                                        self.client1.signing_keys,
                                        note_options,
                                        api_url)
    assert("HTTP 409" in str(excinfo.value))
