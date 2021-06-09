from e3db.exceptions import NoteValidationError
import e3db
import e3db.types as types
import pytest

# these are placeholder values for testing & can be removed on ReadNote is functional.
public_key = '88ph_j2dytMVTBsgCm-9hU608WyJgpB51BuWDQa9AGI'
private_key = 'iCiUo33otFUyyMp_XQZvdSG4S51HG8gypBEhRI_E3W8'
writer_public_signing_key = 'Yn-I-ceRTjVpoJOSOrJvc03R9xT4YV7Sptxo-eQYN5w'
reader_public_signing_key = 'MpSWcRYZqLRzIaxl6sYno7WPy0O6t2vjttkoj_pn_5Y'
writer_public_key = 'c7F5iyzDblgJEIR4Ks7r32YuqOZXD2fW_hPvBCzVEgU'

note_options = types.NoteOptions(
  note_writer_client_id='57b30f55-fcde-4cf6-99ac-2687610d8add',
  max_views=-1,
  id_string='globalNoteName-c5f281bf-65df-4af2-99e9-97fdc890b631',
  expiration='0001-01-01T00:00:00Z',
  expires=False,
  type='',
  plain={},
  file_meta={}
)

note_keys = types.NoteKeys(
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

encrypted_note = types.Note(
  data,
  note_keys,
  note_options
)

class TestNoteSupport():
  def test_decrypt_valid_note_succeeds(self):
    '''
    Asserts that a note with the correct decrypted data is returned.
    '''
    encrypted_note.signature = signature
    decrypted_note = e3db.Client.decrypt_note(encrypted_note, private_key)
    assert(decrypted_note.data['secret'] == 'data')

  def test_decrypt_note_without_signature_fails(self):
    '''
    Asserts that decryption of a note without a signature fails.
    '''
    encrypted_note.signature = ''
    with pytest.raises(NoteValidationError):
      e3db.Client.decrypt_note(encrypted_note, private_key)
  
  def test_decrypt_note_invalid_signing_key_fails(self):
    '''
    Asserrs that decryption fails when the wrong private key is provided.
    '''
    encrypted_note.signature = signature
    with pytest.raises(Exception):
      e3db.Client.decrypt_note(encrypted_note, public_key)