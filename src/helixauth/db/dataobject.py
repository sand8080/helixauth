from helixcore.mapping.objects import Mapped


class ActionLog(Mapped):
    __slots__ = ['id', 'user_id', 'custom_user_info', 'action',
        'request_date', 'remote_addr', 'request', 'response']
    table = 'action_log'


class Environment(Mapped):
    __slots__ = ['id', 'name']
    table = 'environment'


class User(Mapped):
    __slots__ = ['id', 'environment_id', 'login', 'password']
    table = 'user_data'

    def __repr__(self, except_attrs=()):
        return super(User, self).__repr__(except_attrs=except_attrs + ('password',))
