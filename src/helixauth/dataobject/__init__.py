from helixcore.mapping.objects import Mapped


class ActionLog(Mapped):
    __slots__ = ['id', 'user_id', 'custom_user_info', 'action',
        'request_date', 'remote_addr', 'request', 'response']
    table = 'action_log'


class Environment(Mapped):
    __slots__ = ['id', 'name']
    table = 'environment'
