from helixcore import mapping
from helixcore.db.wrapper import EmptyResultSetError
from helixcore.misc import security
from helixcore.server.exceptions import DataIntegrityError, AuthError

from helixbilling.domain.objects import Operator, Currency
from helixbilling.error import BalanceDisabled, OperatorNotFound
from helixbilling.logic.filters import (BalanceFilter, BalanceLockFilter,
    ChargeOffFilter)


def get_operator(curs, o_id, for_update=False): #IGNORE:W0622
    return mapping.get_obj_by_field(curs, Operator, 'id', o_id, for_update)


def get_operator_by_login(curs, login, for_update=False):
    try:
        return mapping.get_obj_by_field(curs, Operator, 'login', login, for_update)
    except EmptyResultSetError:
        raise OperatorNotFound(login)


def get_auth_opertator(curs, login, password, for_update=False):
    try:
        return mapping.get_obj_by_fields(curs, Operator,
            {'login': login, 'password': security.encrypt_password(password)}, for_update)
    except EmptyResultSetError:
        raise AuthError('Access denied.')


def get_currency_by_code(curs, code, for_update=False):
    try:
        return mapping.get_obj_by_field(curs, Currency, 'code', code, for_update)
    except EmptyResultSetError:
        raise DataIntegrityError('Currency  %s is not found' % code)


def get_currency_by_balance(curs, balance, for_update=False):
    return mapping.get_obj_by_field(curs, Currency, 'id', balance.currency_id, for_update)


def get_currencies(curs, ordering_params=None, for_update=False):
    if not ordering_params:
        ordering_params = 'id'
    return mapping.get_list(curs, Currency, None, order_by=ordering_params, for_update=for_update)


def get_currencies_indexed_by_id(curs):
    currencies = get_currencies(curs)
    return dict([(c.id, c) for c in currencies])


def get_balance(curs, operator, customer_id, for_update=False):
    f = BalanceFilter(operator, {'customer_id': customer_id}, {}, None)
    return f.filter_one_obj(curs, for_update=for_update)


def get_active_balance(curs, operator, customer_id, for_update=False):
    balance = get_balance(curs, operator, customer_id, for_update)
    if balance.active is False:
        raise BalanceDisabled(customer_id)
    return balance


def get_balance_lock(curs, operator, customer_id, order_id, for_update=False):
    f = BalanceLockFilter(operator, {'customer_id': customer_id, 'order_id': order_id}, {}, None)
    return f.filter_one_obj(curs, for_update=for_update)


def get_chargeoff(curs, operator, customer_id, order_id, for_update=False):
    f = ChargeOffFilter(operator, {'customer_id': customer_id, 'order_id': order_id}, {}, None)
    return f.filter_one_obj(curs, for_update=for_update)
