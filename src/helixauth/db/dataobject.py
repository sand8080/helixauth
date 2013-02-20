from helixcore.mapping.objects import Mapped, serialize_field
from helixcore.db.dataobject import ActionLog #@UnusedImport


class Environment(Mapped):
    __slots__ = ['id', 'name']
    table = 'environment'


class User(Mapped):
    ROLE_SUPER = 'super'
    ROLE_USER = 'user'
    LANG_EN = 'en'
    LANG_RU = 'ru'
    LANGS = (LANG_EN, LANG_RU)
    __slots__ = ['id', 'environment_id', 'email', 'password', 'salt',
        'is_active', 'role', 'groups_ids', 'lang']
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


class Notification(Mapped):
    TYPE_EMAIL = 'email'
    __slots__ = ['id', 'environment_id', 'event', 'is_active',
        'type', 'serialized_messages']
    table = 'notification'

    def __init__(self, **kwargs):
        d = serialize_field(kwargs, 'messages', 'serialized_messages')
        super(Notification, self).__init__(**d)
