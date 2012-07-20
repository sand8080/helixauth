from helixcore.db.sql import Eq, LessEq, In, Like, AnyOf
from helixcore.db.wrapper import SelectedMoreThanOneRow, ObjectNotFound
from helixcore.db.filters import (ObjectsFilter, InSessionFilter,
    EnvironmentObjectsFilter, ActionLogFilter) #@UnusedImport

from helixauth.db.dataobject import (Environment, Session,
    Service, User, Group)
from helixauth.error import (UserNotFound, EnvironmentNotFound,
    SessionNotFound, GroupNotFound, ServiceNotFound)


class SessionFilter(ObjectsFilter):
    cond_map = [
        ('session_id', 'session_id', Eq),
        ('environment_id', 'environment_id', Eq),
        ('subject_users_ids', 'user_id', In),
        ('to_update_date', 'update_date', LessEq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(SessionFilter, self).__init__(filter_params, paging_params,
            ordering_params, Session)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(SessionFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise SessionNotFound(**self.filter_params)


class EnvironmentFilter(ObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('name', 'name', Eq),
        ('environment_name', 'name', Eq),
        ('environment_id', 'id', Eq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(EnvironmentFilter, self).__init__(filter_params, paging_params,
            ordering_params, Environment)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(EnvironmentFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise EnvironmentNotFound(**self.filter_params)


class UserFilter(InSessionFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('roles', 'role', In),
        ('login', 'login', Like),
        ('password', 'password', Eq),
        ('groups_ids', 'groups_ids', AnyOf),
        ('is_active', 'is_active', Eq),
    ]

    def __init__(self, session, filter_params, paging_params, ordering_params):
        super(UserFilter, self).__init__(session, filter_params,
            paging_params, ordering_params, User)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(UserFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise UserNotFound(**self.filter_params)


class SubjectUserFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('login', 'login', Eq),
        ('password', 'password', Eq),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
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
        ('is_active', 'is_active', Eq),
    ]

    def __init__(self, environment_id, filter_params, paging_params, ordering_params):
        super(GroupFilter, self).__init__(environment_id, filter_params, paging_params,
            ordering_params, Group)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(GroupFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise GroupNotFound(**self.filter_params)


class ServiceFilter(EnvironmentObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('ids', 'id', In),
        ('name', 'name', Eq),
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

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(ServiceFilter, self).filter_one_obj(curs, for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise ServiceNotFound(**self.filter_params)
