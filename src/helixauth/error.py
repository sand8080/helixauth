from helixcore import security
from helixcore.db.wrapper import ObjectNotFound, ObjectCreationError


class HelixauthError(Exception):
    pass


class HelixauthObjectNotFound(HelixauthError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        sanitized_kwargs = security.sanitize_credentials(kwargs)
        super(HelixauthObjectNotFound, self).__init__('%s not found by params: %s' %
            (class_name, sanitized_kwargs))


class HelixauthObjectAlreadyExists(HelixauthError, ObjectCreationError):
    pass


class UserNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(UserNotFound, self).__init__('User', **kwargs)


class SessionNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(SessionNotFound, self).__init__('Session', **kwargs)


class EnvironmentNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(EnvironmentNotFound, self).__init__('Environment', **kwargs)


class UserAuthError(HelixauthError):
    pass


class UserInactive(HelixauthError):
    def __init__(self):
        super(UserInactive, self).__init__('User is inactive')


class SessionExpired(HelixauthError):
    def __init__(self):
        super(SessionExpired, self).__init__('Session expired')
