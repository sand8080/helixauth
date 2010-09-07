from helixcore.db.sql import And, Eq, Like, MoreEq, LessEq
from helixcore.db.wrapper import SelectedMoreThanOneRow, ObjectNotFound
from helixcore.db.filters import ObjectsFilter as OFImpl

from helixauth.db.dataobject import User, Environment, ActionLog
from helixauth.error import UserNotFound, EnvironmentNotFound


class EnvironmentObjectsFilter(OFImpl):
    def __init__(self, environment, filter_params, paging_params, ordering_params, obj_class):
        super(EnvironmentObjectsFilter, self).__init__(filter_params, paging_params, ordering_params, obj_class)
        self.environment = environment


    def _cond_by_filter_params(self):
        cond = super(EnvironmentObjectsFilter, self)._cond_by_filter_params()
        cond = And(cond, Eq('environment_id', self.environment.id))
        return cond


class EnvironmentFilter(OFImpl):
    cond_map = [
        ('name', 'name', Eq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(EnvironmentFilter, self).__init__(filter_params, paging_params, ordering_params, Environment)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(EnvironmentFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise EnvironmentNotFound(**self.filter_params)


class UserFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('login', 'login', Eq),
        ('login_like', 'login', Like),
        ('password', 'password', Eq),
    ]

    def __init__(self, environment, filter_params, paging_params, ordering_params):
        super(UserFilter, self).__init__(environment, filter_params, paging_params,
            ordering_params, User)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(UserFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise UserNotFound(self.filter_params)


class ActionLogFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('action', 'action', Eq),
        ('actor_user_id', 'actor_user_id', Eq),
        ('from_request_date', 'request_date', MoreEq),
        ('to_request_date', 'request_date', LessEq),
    ]

    def __init__(self, environment, filter_params, paging_params, ordering_params):
        super(ActionLogFilter, self).__init__(environment, filter_params,
            paging_params, ordering_params, ActionLog)
