from helixcore.db.sql import And, Eq, Like
from helixcore.db.wrapper import SelectedMoreThanOneRow, ObjectNotFound
from helixcore.db.filters import ObjectsFilter as OFImpl

from helixauth.db.dataobject import User, Environment
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


#class ReceiptFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('from_creation_date', 'creation_date', MoreEq),
#        ('to_creation_date', 'creation_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-creation_date'
#        super(ReceiptFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, Receipt)
#
#
#class BonusFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('from_creation_date', 'creation_date', MoreEq),
#        ('to_creation_date', 'creation_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-creation_date'
#        super(BonusFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, Bonus)
#
#
#class BalanceLockFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('order_id', 'order_id', Eq),
#        ('order_ids', 'order_id', In),
#        ('order_type', 'order_type', Eq),
#        ('order_types', 'order_type', In),
#        ('from_locking_date', 'locking_date', MoreEq),
#        ('to_locking_date', 'locking_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-locking_date'
#        super(BalanceLockFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, BalanceLock)
#
#
#class ChargeOffFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_id', Eq),
#        ('customer_ids', 'customer_id', In),
#        ('order_id', 'order_id', Eq),
#        ('order_ids', 'order_id', In),
#        ('order_type', 'order_type', Eq),
#        ('order_types', 'order_type', In),
#        ('from_locking_date', 'locking_date', MoreEq),
#        ('to_locking_date', 'locking_date', LessEq),
#        ('from_chargeoff_date', 'chargeoff_date', MoreEq),
#        ('to_chargeoff_date', 'chargeoff_date', LessEq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        if ordering_params is None:
#            ordering_params = '-chargeoff_date'
#        super(ChargeOffFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, ChargeOff)
#
#
#class ActionLogFilter(ObjectsFilter):
#    cond_map = [
#        ('customer_id', 'customer_ids', Any),
#        ('action', 'action', Eq),
#        ('from_request_date', 'request_date', MoreEq),
#        ('to_request_date', 'request_date', LessEq),
#        ('remote_addr', 'remote_addr', Eq),
#    ]
#
#    def __init__(self, operator, filter_params, paging_params, ordering_params):
#        super(ActionLogFilter, self).__init__(operator, filter_params, paging_params,
#            ordering_params, ActionLog)
