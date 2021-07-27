from e3db.types.signing_key_pair import SigningKeyPair
from e3db.types.encyption_key_pair import EncryptionKeyPair
import os
from e3db import Client
if 'CRYPTO_SUITE' in os.environ and os.environ['CRYPTO_SUITE'] == 'NIST':
    from .nist_crypto import NistCrypto as Crypto
else:
    from .sodium_crypto import SodiumCrypto as Crypto
from typing import Tuple
from e3db.tsv1_auth import E3DBTSV1Auth
import requests
import json
from .exceptions import APIError, UnsupportedAPIResponse

TOZID_LOGIN_HEADER = "X-TOZID-LOGIN-TOKEN"
DEFAULT_API_URL = "https://api.e3db.com"

class Identity:
    """
    Identity represents a connection to the Tozny Identity service on behalf of a realm.
 
    Before registration, login, or other client creation methods are possible, the configuration
    for a Tozny Identity realm is needed. Identity holds this configuration and provides methods
    for all pre-client operations. In other words, the methods this object make identity clients
    for users that belong to the configured realm. It helps authenticate users.
    
    """

    def __init__(self, config, client_config, agent):
        """
        Initialize the Identity class. This constructor should not be called directly.
        Please use the identity_login method instead

        Parameters
        ----------
        config : dict
            dictionary with config elements unique to this Identity. Config must include values for the following:
            realm_name, realm_domain, app_name, api_url, and user_id
        
        client_config : dict
            A dict that holds the configuration for a storage client. 

        agent : dict
            A dict that holds OAuth values neccessary for a logged in Identity: access_token, token_type,
            refresh_token, expiry, and refresh_expiry
        """
        self.realm_name = config['realm_name']
        self.realm_domain = config['realm_domain']
        self.app_name = config['app_name']
        self.api_url = config['api_url']
        self.user_id = config['user_id']
        self.storage_client = Client(client_config)
        self.access_token = agent['access_token']
        self.token_type = agent['token_type']
        self.refresh_token = agent['refresh_token']
        self.expiry = agent['expiry']
        self.refresh_expiry = agent['refresh_expiry']

    @staticmethod
    def identity_login(user_name: str, password: str, realm_name: str, app_name: str, api_url: str=DEFAULT_API_URL) -> 'Identity':
        """
        A factory method to login an existing user, get the stored identity credentials for a user,
        create a client for them, and return an Identity object.

        The username and password are used to derive encryption keys used to fetch a pre-stored
        note which contains the users identity credentials.

        Only password based realm types are supported at this time.
        Brokered Login is not supported at this time.
        MFA is not supported

        Parameters
        ----------
        user_name : str

        password : str

        realm_name : str
            A case insensitive realm name cam be used here
        
        app_name : str

        api_url: str
            Defaults to https://api.e3db.com

        Returns
        -------
        Identity
            an instance of the Identity Class
        """
        realm_info = get_public_realm_info(realm_name, api_url)
        realm_name = realm_info['name']
        realm_domain = realm_info['domain']
        note_name, key_pair, signing_key_pair = Identity.derive_note_creds(user_name, password, realm_name)
        pkce_verifier, pkce_challenge = Crypto.generate_pkce_challenge()
        auth = E3DBTSV1Auth(signing_key_pair.private_key)

        # PKCE step #1: submit a challenge for this user & Realm
        redirect = pkce_submit_challenge(user_name, realm_domain, app_name, pkce_challenge, auth, api_url)
        
        #PKCE step #2, submit public keys to redirect with session params
        context = pkce_submit_keys(key_pair, signing_key_pair, redirect, auth)    

        # PKCE step #3 make final request for creds using context and verifier
        credentials = pkce_get_credentials(realm_domain, context, pkce_verifier, auth, api_url)
        access_token = credentials["access_token"]

        # Read Id note using our access token 
        stored_creds = Client.read_anonymous_note_by_name(note_name, 
                                                    key_pair.private_key,
                                                    signing_key_pair.private_key,
                                                    auth_headers={ TOZID_LOGIN_HEADER : access_token },
                                                    api_url=api_url)

        return Identity(json.loads(stored_creds.data['config']),
                        json.loads(stored_creds.data['storage']),
                        credentials)

    @staticmethod
    def derive_note_creds(user_name: str, password: str, realm_name: str) -> Tuple[str, EncryptionKeyPair, SigningKeyPair]:
        """
        Derive the note name, crypto, and signing keys for an note containing identity credentials.

        Parameters
        ----------
        user_name : string
            username The username credentials are being derived for.
        
        password : string
           password The secret password for the user.

        realm_name : string
             realmName The identity realm name.
        
        NOTE: Only password based cred_type is supported at this time

        Returns
        -------
        Tuple[string, EncryptionKeyPair, SigningKeyPair]
            Where the base 64 encoded string is the hash of the user name and the realm name
        """
        
        name_seed = f"{user_name.lower()}@realm:{realm_name}"
        note_name_as_bytes = Crypto.hashString(name_seed)
        note_name_as_b64_string = Crypto.base64encode(note_name_as_bytes).decode('utf-8')
        password_bytes = Crypto.to_bytes(password)
        name_seed_bytes = Crypto.to_bytes(name_seed)
        key_pair = Crypto.derive_crypto_keypair(password_bytes, name_seed_bytes)
        salt_in_bytes = Crypto.to_bytes(key_pair.public_key + key_pair.private_key) 
        signing_key_pair = Crypto.derive_signing_keypair(password_bytes, salt_in_bytes)

        return note_name_as_b64_string, key_pair, signing_key_pair

### Helper functions for this module ####

def __response_check(response):
    """
    Raises errors based on response HTTP status code.

    Parameters
    ----------
    response : requests.models.Response
        Response object to get status code from.

    Returns
    -------
    None
    """

    # Map of HTTP error codes to exception messages
    # 401 Unauthorized Maps to Invalid Credentials
    errors = {
        400: APIError('Invalid request: HTTP 400'),
        401: APIError('Invalid credentials: HTTP 401'),
        403: APIError('Unauthorized: HTTP 403'),
        404: APIError('Requested item not found: HTTP 404'),
        429: APIError('Too many requests made to endpoint. HTTP 429. Slow down.')
    }

    # Lookup type of error we should throw, and do so if needed.
    if response.status_code in errors:
        raise errors[response.status_code]

    # If we do not have a pre-formulated error to return, but get another HTTP
    # Error, we check if response is in the 4XX-5XX Range, and return a generic HTTP error
    if response.status_code >= 400 and response.status_code <= 600:
        raise APIError("HTTP Error: {0}".format(response.status_code))

def pkce_submit_challenge(user_name, realm_domain, app_name, pkce_challenge, auth, api_url):
    """ Uses realm_domain value for realm_name key to avoid case sensitivity discrepencies """
    url = f"{api_url}/v1/identity/login"
    body = {
        "username" : user_name,
        "realm_name" : realm_domain,
        "app_name" : app_name,
        "code_challenge" : pkce_challenge.decode('utf-8'),
        "login_style" : "api"
    }
    redirect = requests.post(url=url, auth=auth, json=body)
    __response_check(redirect)
    redirect = redirect.json()
    if redirect["type"] != "continue":
        raise UnsupportedAPIResponse(f"Identity Login failure, expected type 'continue' but found {redirect['type']}")
    return redirect

def pkce_submit_keys(key_pair, signing_key_pair, redirect, auth):
    data = {
        "public_key": key_pair.public_key,
        "public_signing_key": signing_key_pair.public_key
    }
    action_request = requests.post(url=redirect["action_url"], auth=auth, data=data)
    __response_check(action_request)
    action_request = action_request.json()
    if action_request["type"] != "fetch":
        raise UnsupportedAPIResponse(f"Identity Login failure, expected type 'fetch' but found {redirect['type']}")
    return action_request["context"]

def pkce_get_credentials(realm_domain, context, pkce_verifier, auth, api_url):
    """Using realm_domain for value of realm_name to avoid case sesitive discrepencies"""
    body = {
        "realm_name": realm_domain,
        "session_code": context["session_code"],
        "execution": context["execution"],
        "tab_id": context["tab_id"],
        "client_id": context["client_id"],
        "auth_session_id": context["auth_session_id"],
        "code_verifier": pkce_verifier.decode('utf-8'),
    }
    final_response = requests.post(url=f"{api_url}/v1/identity/tozid/redirect", auth=auth, json=body)
    __response_check(final_response)
    return final_response.json()

def get_public_realm_info(realm_name: str, api_url=DEFAULT_API_URL) -> dict:
    """
    A public function to return the realm info object for a given realm name.

    Parameters
    ----------
    realm_name : str
        Case insensitive realm_name
    
    api_url : str
        The base url of the Tozny API. Defaults to "https://api.e3db.com"

    Returns
    -------
    dict
        Key Values of the return object are 'name', 'broker_id' and 'domain'
        The name is case sensitive. 

    """
    resp = requests.get(url=f'{api_url}/v1/identity/info/realm/{realm_name}')
    __response_check(resp)
    return resp.json()
