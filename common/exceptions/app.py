class AppException(Exception):
    pass


class MessageException(AppException):
    pass


class AuthMessageException(MessageException):
    pass


class MessageHeaderException(MessageException):
    pass


class NoOrganizationIdentityException(MessageHeaderException):
    pass
