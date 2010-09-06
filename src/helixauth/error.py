#from helixcore.server.exceptions import ActionNotAllowedError
from helixcore.db.wrapper import ObjectNotFound, ObjectCreationError


class HelixauthError(Exception):
    pass


class HelixauthObjectNotFound(HelixauthError, ObjectNotFound):
    def __init__(self, class_name, **kwargs):
        super(HelixauthObjectNotFound, self).__init__('%s not found by params: %s' %
            (class_name, kwargs))


class HelixauthObjectAlreadyExists(HelixauthError, ObjectCreationError):
    pass


class UserNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(UserNotFound, self).__init__('User', **kwargs)


class EnvironmentNotFound(HelixauthObjectNotFound):
    def __init__(self, **kwargs):
        super(EnvironmentNotFound, self).__init__('Environment', **kwargs)
