class NoInternetConnectionException(Exception):
    """
    Exception indicating no internet connection is present
    """
    pass


class UnauthorizedException(Exception):
    """
    Exception to indicate that access is denied to the cloud api.
    """
    pass


class UnkownCloudException(Exception):
    """
    Exception to indicate that something went wrong in the cloud; possibly an unexpected error was raised in the cloud.
    """
    pass


class BadRequestException(Exception):
    """
    Exception to indicate that the input to the rest-api was incorrect.
    """
    pass
