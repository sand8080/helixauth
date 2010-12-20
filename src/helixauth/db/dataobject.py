from helixcore.mapping.objects import Mapped
import cjson


def serialize_rights(d):
    res = dict(d)
    r = res.pop('rights', '')
    if isinstance(r, list):
        res['serialized_rights'] = cjson.encode(r)
    return res


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'custom_actor_user_info',
        'actor_user_id', 'subject_users_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


class Environment(Mapped):
    __slots__ = ['id', 'name']
    table = 'environment'


class User(Mapped):
    ROLE_SUPER = 'super'
    ROLE_USER = 'user'
    __slots__ = ['id', 'environment_id', 'login', 'password', 'is_active',
        'role']
    table = 'user_data'

    def __repr__(self, except_attrs=()):
        return super(User, self).__repr__(except_attrs=except_attrs + ('password',))


class UserRights(Mapped):
    __slots__ = ['id', 'environment_id', 'user_id', 'serialized_rights']
    table = 'user_rights'


class Group(Mapped):
    __slots__ = ['id', 'environment_id', 'name', 'is_active', 'serialized_rights']
    table = 'group_data'

    def __init__(self, **kwargs):
        d = serialize_rights(kwargs)
        super(Group, self).__init__(**d)


class Session(Mapped):
    __slots__ = ['id', 'session_id', 'environment_id', 'user_id',
        'serialized_data', 'start_date', 'update_date']
    table = 'session'


class Service(Mapped):
    TYPE_AUTH = 'auth'
    TYPE_BILLING = 'billing'
    TYPE_TARIFF = 'tariff'
    __slots__ = ['id', 'environment_id', 'name', 'properties', 'type',
        'is_active', 'is_possible_deactiate']
    table = 'service'


