from helixcore.mapping.objects import Mapped


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'custom_actor_user_info',
        'actor_user_id', 'subject_user_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


class Environment(Mapped):
    __slots__ = ['id', 'name']
    table = 'environment'


class User(Mapped):
    __slots__ = ['id', 'environment_id', 'login', 'password']
    table = 'user_data'

    def __repr__(self, except_attrs=()):
        return super(User, self).__repr__(except_attrs=except_attrs + ('password',))


class Session(Mapped):
    __slots__ = ['id', 'session_id', 'environment_id', 'user_id',
        'serialized_data', 'start_date', 'update_date']
    table = 'session'
