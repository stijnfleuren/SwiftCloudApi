import socket
from collections import Callable

from swift_cloud_py.common.errors import NoInternetConnectionException


def has_internet_connection() -> bool:
    """
    test whether a working internet connection is present
    :return: boolean indicating presence of working internet connection
    """

    # test if we could connect to either one of the following websites; it is highly improbable that all of them
    # are down.
    for website in ["www.google.com", "www.amazon.com"]:
        try:
            host = socket.gethostbyname(website)
            s = socket.create_connection((host, 80), 2)
            s.close()
            return True  # connection was established; assuming internet connection is available
        except socket.gaierror:  # could not establish connection with the website
            pass

    return False  # no connection could be established; assuming not internet connection is available


def ensure_has_internet(func: Callable) -> Callable:
    """
    wrapper function that can be used as a decorator around the methods of SwiftMobilityCloudApi; it ensures that an
     internet connection is present (if not an error is raised).
    :param func: method of SwiftMobilityCloudApi.
    :return: wrapped method.
    """
    # args and kwargs to allow for methods that have multiple named and unnamed arguments
    def wrapper(*args, **kwargs):
        if not has_internet_connection():
            raise NoInternetConnectionException()
        return func(*args, **kwargs)

    return wrapper
