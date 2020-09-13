import os


class Credentials:
    """
    credentials retrieved from environment variables
    """
    def __init__(self):
        # swift mobility cloud credentials from environment variables to prevent hard-coding credentials
        self._access_key = os.environ.get("smc_api_key")
        self._secret_access_key = os.environ.get("smc_api_secret")

    @property
    def access_key(self):
        return self._access_key

    @property
    def secret_access_key(self):
        return self._secret_access_key
