from math import log10
from decimal import Decimal
from helixcore.server.exceptions import ActionNotAllowedError
from helixcore.utils import filter_dict


def decimal_to_cents(currency, dec):
    int_part = int(dec)
    prec = int(round(log10(currency.cent_factor)))
    cent_part = int((dec - int_part) * 10 ** prec)
    return currency.cent_factor * int_part + cent_part


def cents_to_decimal(currency, cents):
    prec = int(round(log10(currency.cent_factor)))
    format = '%%d.%%0%dd' % prec
    int_part = cents / currency.cent_factor
    cent_part =  cents % currency.cent_factor
    return Decimal(format % (int_part, cent_part))


def decimal_texts_to_cents(data, currency, amount_fields):
    result = dict(data)
    amount_data = filter_dict(amount_fields, data)
    for k, v in amount_data.items():
        amount_data[k] = decimal_to_cents(currency, Decimal(v))
    result.update(amount_data)
    return result


def get_lockable_amounts(balance):
    return {
        'available_real_amount': balance.available_real_amount + balance.overdraft_limit,
        'available_virtual_amount': balance.available_virtual_amount
    }


def compute_locks(currency, balance, lock_amount):
    """
    Returns {field_name: locked_amount}. field_names are from locking_order.
    If locking_order is None, then default locking order used: [available_real_amount, available_real_amount].

    If balance has overdraft_limit > 0 and available_real_amount is in locking_order or locking_order is None,
    then we can decrease available_real_amount until reach -overdraft_limit value.

    ActionNotAllowedError exception raises if money not enough.
    """
    if balance.locking_order is None:
        locking_order = ['available_real_amount', 'available_virtual_amount']
    else:
        locking_order = balance.locking_order

    locked_amounts = dict([(a, 0) for a in locking_order])
    lockable_amounts = get_lockable_amounts(balance)

    remain_to_lock = lock_amount
    for amount_name in locking_order:
        if remain_to_lock <= 0:
            break
        available_to_lock = min(remain_to_lock, lockable_amounts[amount_name])
        locked_amounts[amount_name] += available_to_lock

        remain_to_lock -= available_to_lock
        lockable_amounts[amount_name] -= available_to_lock

    if remain_to_lock > 0:
        def human_amount(a):
            return '%s %s' % (cents_to_decimal(currency, a), currency.code)
        lockable_descr = []
        for name, avail in get_lockable_amounts(balance).items():
            descr = '%s: %s' % (name, human_amount(avail))
            lockable_descr.append(descr)
        error = {
            'lock_amount': human_amount(lock_amount),
            'customer_id': balance.customer_id,
            'lockable_descr': ', '.join(lockable_descr),
        }
        raise ActionNotAllowedError(
            'Can not lock %(lock_amount)s on balance of customer %(customer_id)s. '
            'Available to lock: %(lockable_descr)s' % error
        )
    return locked_amounts
