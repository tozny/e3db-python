from re import T
from e3db import Client
from e3db.types.signing_key_pair import SigningKeyPair
from e3db.types.encyption_key_pair import EncryptionKeyPair
from e3db.identity import *
import os
from e3db.sodium_crypto import SodiumCrypto as Crypto
from e3db.tsv1_auth import E3DBTSV1Auth
import responses

token = os.environ["REGISTRATION_TOKEN"]
api_url = os.environ["DEFAULT_API_URL"]

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

    # assert deriving note creds is a pure function
    hashed_name2, key_pair2, signing_pair2 = Identity.derive_note_creds(user_name, password, realm_name)
    assert(hashed_name == hashed_name2)
    assert(key_pair.private_key == key_pair2.private_key)
    assert(signing_pair.private_key == signing_pair2.private_key)

@responses.activate
def test_pkce_submit_challenge():

    resp = {'login_action': True, 
                'type': 'continue',
                'action_url': 'http://fakeredirect.com',
                'content_type': 'application/x-www-form-urlencoded'}
    responses.add(responses.POST, f"{api_url}/v1/identity/login",
                  json=resp, status=200)


    user_name = "bar"
    password = "someverylongpasswordphraseyouwillneverguess"
    realm_name = "somerealm"
    app_name = "does not exist"
    realm_name = realm_name.lower()
    note_name, key_pair, signing_key_pair = Identity.derive_note_creds(user_name, password, realm_name)
    pkce_verifier, pkce_challenge = Crypto.generate_pkce_challenge()
    auth = E3DBTSV1Auth(signing_key_pair.private_key)
    
    redirect = pkce_submit_challenge(user_name, realm_name, app_name, pkce_challenge, auth, api_url)
    assert type(redirect) == dict
    assert redirect == resp
    assert len(responses.calls) == 1

@responses.activate
def test_pkce_submit_keys():
    user_name = "bar"
    password = "someverylongpasswordphraseyouwillneverguess"
    realm_name = "somerealm"
    _, key_pair, signing_key_pair = Identity.derive_note_creds(user_name, password, realm_name)
    auth = E3DBTSV1Auth(signing_key_pair.private_key)
    fake_url = "https://myveryfakeredirect.com"
    challenge_response = {
        'login_action': True, 
        'type': 'continue',
        'action_url': fake_url,
        'content_type': 'application/x-www-form-urlencoded'}
    resp = {
        'login_action': True,
        'type': 'fetch',
        'action_url': 'http://someurlandparams.com',
        'fields': {},
        'context': {
            'execution': 'api_login_complete',
            'tab_id': 'some_id',
            'session_code': 'some_code',
            'auth_session_id': '123-abc',
            'client_id': 'tozid-realm-idp'},
        'content_type': 'application/x-www-form-urlencoded'}
    responses.add(responses.POST, fake_url, json=resp, status=200)
    context = pkce_submit_keys(key_pair, signing_key_pair, challenge_response, auth)
    assert type(context) == dict
    assert context == resp['context']
    assert len(responses.calls) == 1
    assert responses.calls[0].request.body == f"public_key={key_pair.public_key}&public_signing_key={signing_key_pair.public_key}"

@responses.activate
def test_pkce_get_credentials():
    user_name = "baz"
    password = "someverylongpassphraseyouwillneverguess"
    realm_name = 'hyrule'
    verifier, _ = Crypto.generate_pkce_challenge()
    _, _, signing_key_pair = Identity.derive_note_creds(user_name, password, realm_name)
    auth = E3DBTSV1Auth(signing_key_pair.private_key)
    context = {'execution': 'api_login_complete',
                'tab_id': 'some_id',
                'session_code': 'some_code',
                'auth_session_id': '123-abc',
                'client_id': 'tozid-realm-idp'}
    resp = {'access_token': 'averylongtoken',
                        'token_type': 'bearer', 'refresh_token': 'moretoken',
                        'expiry': '2021-07-14T01:51:06.3415312Z', 
                        'refresh_expiry': '2021-07-15T00:51:06.3415709Z'}
    responses.add(responses.POST, f"{api_url}/v1/identity/tozid/redirect",
                    json=resp, status=200)
    credentials = pkce_get_credentials(realm_name, context, verifier, auth, api_url)
    assert type(credentials) == dict
    assert credentials == resp
    assert len(responses.calls) == 1

@responses.activate
def test_identity_login_mocked():
    realm_name = "mushroomkingdom"
    realm_info = {
        'name' : realm_name,
        'domain' : realm_name.lower()
    }
    responses.add(responses.GET, f'{api_url}/v1/identity/info/realm/{realm_name}',
                    json=realm_info, status=200)
    user_name = "foo"
    password = "correcthorsebatterystaple"
    app_name = "account"
    note_name, _, _ = Identity.derive_note_creds(user_name, password, realm_name)

    redirect_url = 'http://fakeredirect.com'
    challenge_resp = {'login_action': True, 
                    'type': 'continue',
                    'action_url': redirect_url,
                    'content_type': 'application/x-www-form-urlencoded'}
    responses.add(responses.POST, f"{api_url}/v1/identity/login",
                  json=challenge_resp, status=200)

    final_url = 'http://someurlandparams.com'
    redirect_resp = {'login_action': True, 'type': 'fetch',
        'action_url': final_url, 'fields': {},
        'context': {
            'execution': 'api_login_complete',
            'tab_id': 'some_id',
            'session_code': 'some_code',
            'auth_session_id': '123-abc',
            'client_id': 'tozid-realm-idp'},
        'content_type': 'application/x-www-form-urlencoded'}
    responses.add(responses.POST, redirect_url, json=redirect_resp, status=200)

    
    final_resp = {'access_token': 'averylongtoken',
                        'token_type': 'bearer', 'refresh_token': 'moretoken',
                        'expiry': '2021-07-14T01:51:06.3415312Z', 
                        'refresh_expiry': '2021-07-15T00:51:06.3415709Z'}
    responses.add(responses.POST, f"{api_url}/v1/identity/tozid/redirect",
                    json=final_resp, status=200)

    encrypted_note = {
        "note_id":"b63ee3db-cbc7-4b92-ad77-45c18134ec0a",
        "id_string":"Ar4q8oPRFBMaZWsgMDUg7fZoySa3T4bmhiUnSA54Flo",
        "client_id":"af54af02-293f-4c71-8415-d96c892550ea",
        "mode":"Sodium",
        "recipient_signing_key":"n7bbjHIsa4w7Iu4APiKbYSc2H1upLtNg5-75wAaxBCw",
        "writer_signing_key":"SrFOxDoogO-fUvIN2dfb7r5pqhbZrYZvQddZb5qU3m8",
        "writer_encryption_key":"PjHL3VRAZNlFoCJO2ft4cwtvz2j45yOlhp6nivxq328",
        "encrypted_access_key":"vGl6B2MZzrRdSs_9-XgLayGIjI39fioU3TYarya6-HxNAf8d-cERo4AaQoXj66ax.tpQhmdAkdTYuXxCk_27wqXYVpSCVPq48",
        "type":"",
        "data":{
            "config":"nChjElEQz2MilFBlADbHDbpfp9TXn7MNpMwEbYiqngDNfYdmOfBo5STCEAC2ZbhC.-J4bC2PbqPjYJMSAm_oS3ZxinmbBmPCl.f7dolFNgDW5WqsGa0DaRkYkGWcuHwep7yTARKBnVJ6lqKoJEUuUzKivwk0CUR9g0foKBb0zum908mNgjkh2JMbiFGquOfQX3uPlVEcUhDexQLR8YN7ANDMS3-1xSkryKFofXYzXDK7pZuEGpGt2pzCx8iydRKgXKuvBnPuSRMKIG_EmlZd7zV2_JsA-JsWpjLrHXf2MRp4NrI1Bs0w6cRrs5io1LBkE46buS5uJd6TtUq3d98OL9qwMIAKJ2NcvWao9b96a_KCMWeWTUgJ5JAMBVf5x6ze4mL8HJINV16AeFZ0zDEZwmGP-GAPH4lgvfSdUaKqOCcpEBNeVOGyxxJ1qLfGzL3DWTz8DlRpoQ6Ai1IGcwgDyU62dWzSCOZkVecIzABeIP0v_6hu0VMZX6XMwgvYuEvAlgq9rsVvTMZJggEFjLwRu0to927iiw8Kvsrgm1CW7dZeqtfM_42Fes90AY2ctijA_92H7xH_OMOHT3RN4zIgS7-Zh8UPAT_pJ0QErlnx6b02_Pxw.Hmzcg0cISISH9ZIcBCYF6GWwzn4VimrH",
            "storage":"MEIeF_TDC0tt_FEK9vPuHbTp8p9SMyUTPuS69P6IYlRqcz4chdnEFMUYUN5hgTBi.nH1us1fU2dzz7cCUmnWW6yAllSy06qw3.JWiGw346XjvthKkCZQTvq0LiHbk-Fgz1J-3F0fAGX5D-D1QlNAIAp28svbsuTmTVXcOEGqv7Eklq7RlsBIokwg367y2ARip50sPHHHyboWa46Wj9EDDH6rOU9k2RzJ9gTYonCZ0m-YoZ3Reqt7fp5QzMNXfRQ814N7usL2cVXYWukmDHbI9K1NG3gX02rV5qL4JOQBJQDn1AGvC2hZfgf4onJhe9AMAPH5DJmKkHrP0aq8lzdHLsaXm2qi6e13wfZqmJs8NC7n15WRNcuHPTSV7YaVqx_xx1Yy9fIQsLg1wZ36g9pEaFJd6tSuBDtGNC27cNIoyqH-D-sLtv4iKRFLKCnbNemUxRNySVEGg5JM-NvDZkCsi_wU3YdBC9foWOLRjkTHS6A8b-1NCCSg2_5RN4cLVLUHEaTAlrRbF2-AGHoVOGGsjaC8eu-7Gf3B6EqlfN0MFKHwV-KML0JUgBfvP3W0v8b779Wnoxbr1MLBPq2r3LGExsSlVLprvgnHmHMC-wAmtf1JCo-QfTPMnHbYEzTSBGnro90OV4qhE6vCYVJfNmePa9dVp02sw12AvHdsbe68yFOSeGIAb3fq8Q4-KODEc-w68CNfVsdB8qDq8u37SFzC2E2I0zT0Uu0MRSjLIlBbC3GaTMjXW08lH0AXnzoDPaaXPNZc8oJHWs4vdL7UqkfUmosP0UHD7rngFroq_gj4Z1VH6F4zTmltzv8nSlSbz9_BskN9ekkdm3MfvH9aZ3jXo0j7_f8bwPd74DjCQB7YV4VdDuvYRubTMX_LKbuj10gEHV8a8ANzBju1fUsd_PNkkNITgg_I6djqqV5TEztOHM5XNF3qOdW4MOVR_5otYZ5yIj-kc6VGYaNiZRFP1QgljzGJU111HpMuDSjLgQshpaM_FafO7_xbdc54x7c6CkruQyUAZKil_EBNAkaqD4E_9GSZHk9vI4ChZJJe0iLaoKdgJ10xNEH9CCm7VQcYN4DtPYTMhI0nM.A758nxAArRXHV9EAfm2ISMwbL8PvSGAz"
        },
        "plain":{},
        "signature":"e7737e7c-1637-511e-8bab-93c4f3e26fd9;9eb229ce-5053-441c-b7b9-964f6b403341;86;rMya1gvoEnhNLa1GDNr00B4IpyXjw9Kglb1tbdl3ZoHj7c7xm8WL4TtoFyAQM9Ciu75vxGpuum3AxEu_JHJNDw5a58de71-a335-401e-8d3a-f32c2c7a72cd",
        "created_at":"2021-07-12T19:49:12.738703Z",
        "max_views":-1,
        "views":0,
        "expiration":"0001-01-01T00:00:00Z"}
    responses.add(responses.GET, f'{api_url}/v2/storage/notes?id_string={note_name}',
                    json=encrypted_note, status=200)

    my_identity = Identity.identity_login(user_name, password, realm_name, app_name, api_url)
    assert type(my_identity) == Identity
    assert type(my_identity.storage_client) == Client

    assert len(responses.calls) == 5

def test_init_identity():
    config = {
        "realm_name":"mushroomkingdom",
        "realm_domain":"mushroomkingdom",
        "app_name":"account",
        "api_url":"https://api.e3db.com",
        "user_id":2,
        "broker_target_url":"http://localhost:8081/mushroomkingdom/recover"}
    
    storage = {
        "version":2,
        "api_url":"http://platform.local.tozny.com:8000",
        "api_key_id":"11fb390ed3e0e0283740617f6d5a01d1e9359bf3d353436a4c4f37806871c018",
        "api_secret":"38e5088e0ddc8091bc70eb47026c5b495ba77f5afe145324c6b966ab21bd940b",
        "client_id":"af54af02-293f-4c71-8415-d96c892550ea",
        "public_key":"PjHL3VRAZNlFoCJO2ft4cwtvz2j45yOlhp6nivxq328",
        "private_key":"uOx2S3wciLa328Bt5B0LwabjkJz8Z--WiAngAt4QEpA",
        "public_signing_key":"SrFOxDoogO-fUvIN2dfb7r5pqhbZrYZvQddZb5qU3m8",
        "private_signing_key":"mvulcHTMuvZkuAcRVOpVUQMikMY6gQxy7fG4_ORYvtJKsU7EOiiA759S8g3Z19vuvmmqFtmthm9B11lvmpTebw"}

    agent = {
        'access_token': 'averylongtoken',
        'token_type': 'bearer', 'refresh_token': 'moretoken',
        'expiry': '2021-07-14T01:51:06.3415312Z', 
        'refresh_expiry': '2021-07-15T00:51:06.3415709Z'}
    
    my_identity = Identity(config, storage, agent)
    assert type(my_identity) == Identity
    assert type(my_identity.storage_client) == Client
    assert my_identity.realm_name == config['realm_name']
