from helixcore.db.sql import And, Eq, MoreEq, LessEq, In, Like, AnyOf
from helixcore.db.wrapper import SelectedMoreThanOneRow, ObjectNotFound
from helixcore.db.filters import ObjectsFilter as OFImpl

from helixauth.db.dataobject import (Environment, ActionLog, Session,
    Service, User, UserRights, Group)
from helixauth.error import UserNotFound, EnvironmentNotFound, SessionNotFound,\
    GroupNotFound


class EnvironmentObjectsFilter(OFImpl):
    def __init__(self, environment_id, filter_params, paging_params, ordering_params, obj_class):
        super(EnvironmentObjectsFilter, self).__init__(filter_params, paging_params, ordering_params, obj_class)
        self.environment_id = environment_id

    def _cond_by_filter_params(self):
        cond = super(EnvironmentObjectsFilter, self)._cond_by_filter_params()
        cond = And(cond, Eq('environment_id', self.environment_id))
        return cond


class InSessionFilter(OFImpl):
    def __init__(self, session, filter_params, paging_params, ordering_params, obj_class):
        super(InSessionFilter, self).__init__(filter_params, paging_params, ordering_params, obj_class)
        self.session = session

    def _cond_by_filter_params(self):
        cond = super(InSessionFilter, self)._cond_by_filter_params()
        cond = And(cond, Eq('environment_id', self.session.environment_id))
        return cond


class SessionFilter(OFImpl):
    cond_map = [
        ('session_id', 'session_id', Eq),
        ('environment_id', 'environment_id', Eq),
        ('subject_users_ids', 'user_id', In),
        ('to_update_date', 'update_date', MoreEq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(SessionFilter, self).__init__(filter_params, paging_params,
            ordering_params, Session)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(SessionFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise SessionNotFound(**self.filter_params)


class EnvironmentFilter(OFImpl):
    cond_map = [
        ('id', 'id', Eq),
        ('name', 'name', Eq),
        ('environment_name', 'name', Eq),
        ('environment_id', 'id', Eq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(EnvironmentFilter, self).__init__(filter_params, paging_params, ordering_params, Environment)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(EnvironmentFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise EnvironmentNotFound(**self.filter_params)


class UserFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('login', 'login', Like),
        ('password', 'password', Eq),
        ('groups_ids', 'groups_ids', AnyOf),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(UserFilter, self).__init__(session, filter_params, paging_params,
            ordering_params, User)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(UserFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise UserNotFound(**self.filter_params)


class SubjectUserFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('login', 'login', Eq),
        ('password', 'password', Eq),
    ]

    def __init__(self, environment_id, filter_params, paging_params,ordering_params):
        super(SubjectUserFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, User)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(SubjectUserFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise UserNotFound(**self.filter_params)


class GroupFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('name', 'name', Like),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(GroupFilter, self).__init__(environment_id, filter_params, paging_params,
            ordering_params, Group)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(GroupFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise GroupNotFound(**self.filter_params)



class ActionLogFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('action', 'action', Eq),
        ('actor_user_id', 'actor_user_id', Eq),
        ('from_request_date', 'request_date', MoreEq),
        ('to_request_date', 'request_date', LessEq),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(ActionLogFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, ActionLog)


class ServiceFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('name', 'name', Eq),
        ('ids', 'id', In),
        ('types', 'type', In),
        ('is_active', 'is_active', Eq),
        ('type', 'type', Like),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(ServiceFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, Service)

    def indexed_by_id(self, curs):
        ss = self.filter_objs(curs)
        return dict([(s.id, s) for s in ss])


class UserRightsFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('user_id', 'user_id', Eq),
        ('services_ids', 'user_id', In),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(UserRightsFilter, self).__init__(environment_id,
            filter_params, paging_params, ordering_params, UserRights)
