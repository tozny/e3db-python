class EncryptionKeyPair(): 
    
    def __init__(self, public_key, private_key):
        """
        Base64URL encoded representation of a public/private keypair

        Parameters
        ----------
        public_key : str
            Base64 encoded public key 

        private_key : str
            Base64 encoded private key

        Returns
        -------
        None
        """
        self.public_key  = public_key
        self.private_key = private_key
