import logging
from collections import Callable
from time import time

import requests

from swift_cloud_py.common.errors import UnauthorizedException, UnknownAuthenticationException, \
    NoInternetConnectionException, BadRequestException
from swift_cloud_py.authentication.check_internet_connection import has_internet_connection
from swift_cloud_py.authentication.credentials import Credentials


AUTHENTICATION_URL = "https://authentication.swiftmobility.eu/authenticate"


class Authentication:
    """
    Class to retrieve authentication token (jwt token).
    """
    _credentials = Credentials()  # credentials from environment variables
    _jwt_token = None  # last retrieved jwt token
    _exp = time()  # time at which the token expires (in seconds starting from January 1, 1970, 00:00:00 (UTC))

    @classmethod
    def get_authentication_token(cls) -> str:
        """ get a valid jwt token
        return: jwt-token
        """
        # if authentication token not yet set or almost expired
        if cls._jwt_token is None or time() + 30 > cls._exp:
            cls.update_authentication_token()

        return Authentication._jwt_token

    @classmethod
    def update_authentication_token(cls) -> None:
        """
        update the jwt token (store the info in _jwt_token and _exp)
        :return: -
        """
        # check if credentials are set (via environment variables)
        if cls._credentials.access_key is None:
            raise UnauthorizedException("Environment variable smc_api_key is not set")
        elif cls._credentials.secret_access_key is None:
            raise UnauthorizedException("Environment variable smc_api_secret is not set")
        try:
            logging.debug("updating authentication token")
            r = requests.post(url=AUTHENTICATION_URL,
                              json={"accessKey": cls._credentials.access_key,
                                    "secretAccessKey": cls._credentials.secret_access_key,
                                    "accountType": "cloud-api"})
            logging.debug("authentication token updated")
        except requests.exceptions.ConnectionError:  # no connection could be established
            if has_internet_connection():
                logging.debug("updating authentication token failed: unkown exception")
                raise UnknownAuthenticationException
            else:
                logging.debug("updating authentication token failed: no internet!")
                raise NoInternetConnectionException

        if r.status_code != 200:
            # no success; here we also catch the errors {"error": {"code": status_code, "message": error_message}}
            if not has_internet_connection():
                raise NoInternetConnectionException
            elif r.status_code == 401:
                raise UnauthorizedException("Access was denied; check if the environment variables 'smc_api_key' and"
                                            "smc_secret_key' are correctly set. If still not working, send "
                                            "a mail to cloud_api@swiftmobility.eu")
            elif r.status_code == 400:
                # error status_codes:
                # 400: wrong input
                # 403: not authorized
                # 500: server error
                raise BadRequestException  # incorrect json format send to endpoint
            else:
                raise UnknownAuthenticationException
        else:
            # store info of new token
            json_dict = r.json()
            cls._jwt_token = json_dict["jwt-token"]
            cls._exp = int(json_dict["exp"])


def authenticate(func: Callable) -> Callable:
    """
    wrapper function that can be used as a decorator around the methods of SwiftMobilityCloudApi; it ensures that the
     _authentication_token field of SwiftMobilityCloudApi is up-to-date.
    :param func: method of SwiftMobilityCloudApi
    :return: wrapped method
    """
    # args and kwargs to allow for methods that have multiple named and unnamed arguments
    def wrapper(api, *args, **kwargs):
        api._authentication_token = Authentication.get_authentication_token()
        return func(api, *args, **kwargs)

    return wrapper
