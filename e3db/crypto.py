

def base64decode(x):
    # From https://stackoverflow.com/a/9956217
    # Python base64 implementation requires padding, which may not be present in the
    # encoded public/private keypair
    return base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))
