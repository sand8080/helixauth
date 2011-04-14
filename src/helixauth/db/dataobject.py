import cjson

from helixcore.mapping.objects import Mapped


def serialize_field(d, f_src_name, f_dst_name):
    res = dict(d)
    if isinstance(res.get(f_src_name), list):
        v = res.pop(f_src_name)
        res[f_dst_name] = cjson.encode(v)
    return res


def deserialize_field(d, f_src_name, f_dst_name):
    res = dict(d)
    if isinstance(res.get(f_src_name), (str, unicode)):
        v = res.pop(f_src_name)
        res[f_dst_name] = cjson.decode(v)
    return res


class ActionLog(Mapped):
    __slots__ = ['id', 'environment_id', 'session_id',
        'custom_actor_user_info', 'actor_user_id',
        'subject_users_ids', 'action', 'request_date',
        'remote_addr', 'request', 'response']
    table = 'action_log'


class Environment(Mapped):
    __slots__ = ['id', 'name']
    table = 'environment'


class User(Mapped):
    ROLE_SUPER = 'super'
    ROLE_USER = 'user'
    __slots__ = ['id', 'environment_id', 'login', 'password', 'salt',
        'is_active', 'role', 'groups_ids']
    table = 'user_data'

    def __repr__(self, except_attrs=()):
        return super(User, self).__repr__(except_attrs=except_attrs + ('password', 'salt'))


class Group(Mapped):
    __slots__ = ['id', 'environment_id', 'name', 'is_active', 'serialized_rights']
    table = 'group_data'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'rights', 'serialized_rights')
        super(Group, self).__init__(**d)


class Session(Mapped):
    __slots__ = ['id', 'session_id', 'environment_id', 'user_id',
        'serialized_data', 'start_date', 'update_date']
    table = 'session'


class Service(Mapped):
    TYPE_AUTH = 'auth'
    TYPE_BILLING = 'billing'
    TYPE_TARIFF = 'tariff'
    __slots__ = ['id', 'environment_id', 'name', 'serialized_properties',
        'type', 'is_active', 'is_possible_deactiate']
    table = 'service'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'properties', 'serialized_properties')
        super(Service, self).__init__(**d)
