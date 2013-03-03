from helixcore import security
from helixcore.db.wrapper import ObjectNotFound, ObjectCreationError

from helixauth import error_code


class HelixauthError(Exception):
    code = error_code.HELIXAUTH_ERROR


class HelixauthObjectNotFound(HelixauthError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        sanitized_kwargs = security.sanitize_credentials(kwargs)
        super(HelixauthObjectNotFound, self).__init__("%s not found by params: %s" %
            (class_name, sanitized_kwargs))
        self.code = error_code.HELIXAUTH_OBJECT_NOT_FOUND


class HelixauthObjectAlreadyExists(HelixauthError, ObjectCreationError):
    def __init__(self, *args, **kwargs):
        super(HelixauthObjectAlreadyExists, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_OBJECT_ALREADY_EXISTS


class UserNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(UserNotFound, self).__init__("User", **kwargs)


class SuperUserCreationDenied(HelixauthObjectNotFound):
    def __init__(self, *args, **kwargs):
        super(SuperUserCreationDenied, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_SUPERUSER_CREATION_DENIED


class SuperUserModificationDenied(HelixauthError):
    def __init__(self, *args, **kwargs):
        super(SuperUserModificationDenied, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_SUPERUSER_MODIFICATION_DENIED


class UserWrongOldPassword(HelixauthError):
    def __init__(self, *args, **kwargs):
        super(UserWrongOldPassword, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_USER_WRONG_OLD_PASSWORD


class UserNewPasswordNotSet(HelixauthError):
    def __init__(self, *args, **kwargs):
        super(UserNewPasswordNotSet, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_NEW_PASSWORD_NOT_SET


class ServiceNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(ServiceNotFound, self).__init__("Service", **kwargs)
        self.code = error_code.HELIXAUTH_SERVICE_NOT_FOUND


class ServiceDeactivationError(HelixauthError):
    def __init__(self, service_name):
        super(ServiceDeactivationError, self).__init__(
            "Service %s can't be deactivated" % service_name)
        self.code = error_code.HELIXAUTH_SERVICE_DEACTIVATION_ERROR


class ServiceDeletionError(HelixauthError):
    def __init__(self, service_type):
        super(ServiceDeletionError, self).__init__(
            "Service of type %s can\'t be deleted" % service_type)
        self.code = error_code.HELIXAUTH_SERVICE_DELETION_ERROR


class SessionNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(SessionNotFound, self).__init__("Session", **kwargs)
        self.code = error_code.HELIXAUTH_SESSION_NOT_FOUND


class EnvironmentNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(EnvironmentNotFound, self).__init__("Environment", **kwargs)
        self.code = error_code.HELIXAUTH_ENVIRONMENT_NOT_FOUND


class UserAuthError(HelixauthError):
    def __init__(self, *args, **kwargs):
        super(UserAuthError, self).__init__(*args, **kwargs)
        self.code = error_code.HELIXAUTH_USER_AUTH_ERROR


class UserAccessDenied(HelixauthError):
    def __init__(self, service_type, prop):
        super(UserAccessDenied, self).__init__("Access denied to service %s property %s" %
            (service_type, prop))
        self.code = error_code.HELIXAUTH_USER_ACCESS_DENIED


class UserInactive(HelixauthError):
    def __init__(self):
        super(UserInactive, self).__init__("User is inactive")
        self.code = error_code.HELIXAUTH_USER_INACTIVE


class SessionExpired(HelixauthError):
    def __init__(self):
        super(SessionExpired, self).__init__('Session expired')
        self.code = error_code.HELIXAUTH_SESSION_EXPIRED


class SessionIpChanged(HelixauthError):
    def __init__(self):
        super(SessionIpChanged, self).__init__("Session ip changed")
        self.code = error_code.HELIXAUTH_SESSION_IP_CHANGED


class SessionTooLargeFixedLifetime(HelixauthError):
    def __init__(self):
        super(SessionTooLargeFixedLifetime, self).__init__("Session fixed lifetime to large")
        self.code = error_code.HELIXAUTH_SESSION_IP_CHANGED


class GroupAlreadyExists(HelixauthObjectAlreadyExists):
    def __init__(self, name):
        super(GroupAlreadyExists, self).__init__("Group %s already exists" % name)
        self.code = error_code.HELIXAUTH_GROUP_ALREADY_EXISTS


class GroupNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(GroupNotFound, self).__init__("Group", **kwargs)
        self.code = error_code.HELIXAUTH_GROUP_NOT_FOUND


class NotificatonNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(NotificatonNotFound, self).__init__("Notification", **kwargs)
        self.code = error_code.HELIXAUTH_GROUP_NOT_FOUND


class NotificatoinPreparingError(HelixauthError):
    pass
