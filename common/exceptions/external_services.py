class ExternalServiceException(Exception):
    pass


class ExternalServiceNotReady(ExternalServiceException):
    pass
