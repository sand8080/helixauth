from helixcore import security
from helixcore.db.wrapper import ObjectNotFound, ObjectCreationError

from helixauth import error_code


class HelixauthError(Exception):
    code = error_code.HELIXAUTH_ERROR


class HelixauthObjectNotFound(HelixauthError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        sanitized_kwargs = security.sanitize_credentials(kwargs)
        super(HelixauthObjectNotFound, self).__init__('%s not found by params: %s' %
            (class_name, sanitized_kwargs))
        self.code = error_code.HELIXAUTH_OBJECT_NOT_FOUND


class HelixauthObjectAlreadyExists(HelixauthError, ObjectCreationError):
    def __init__(self, *args, **kwargs):
        super(HelixauthObjectAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_OBJECT_ALREADY_EXISTS


class UserNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(UserNotFound, self).__init__('User', **kwargs)
#        self.code =


class ServiceDeactivationError(HelixauthError):
    def __init__(self, service_name):
        super(ServiceDeactivationError, self).__init__(
            'Service %s can\'t be deactivated' % service_name)


class SessionNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(SessionNotFound, self).__init__('Session', **kwargs)


class EnvironmentNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(EnvironmentNotFound, self).__init__('Environment', **kwargs)


class UserAuthError(HelixauthError):
    pass


class UserAccessDenied(HelixauthError):
    def __init__(self, login, property):
        raise UserAuthError("User %s access denied to %s" %
            (login, property))


class UserInactive(HelixauthError):
    def __init__(self):
        super(UserInactive, self).__init__('User is inactive')


class SessionExpired(HelixauthError):
    def __init__(self):
        super(SessionExpired, self).__init__('Session expired')
