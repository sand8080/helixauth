from decimal import Decimal
from functools import partial

from helixcore import mapping
from helixcore.db.wrapper import ObjectCreationError, SelectedMoreThanOneRow
from helixcore import utils
from helixcore.server.response import response_ok
from helixcore.server.exceptions import ActionNotAllowedError, AuthError,\
    DataIntegrityError
from helixcore.server.errors import RequestProcessingError
from helixcore.misc import security

from helixbilling.conf.db import transaction
from helixbilling.domain.objects import (Balance, Receipt, BalanceLock,
    Bonus, ChargeOff, Operator)
from helixbilling.error import (BalanceNotFound, CurrencyNotFound, ObjectNotFound,
    BalanceDisabled, OperatorAlreadyExists)

from helixbilling.logic.helper import compute_locks
from helixbilling.logic import selector
from helixbilling.logic.helper import cents_to_decimal, decimal_texts_to_cents
from helixbilling.logic.filters import (BalanceFilter, ReceiptFilter, BonusFilter,
    BalanceLockFilter, ChargeOffFilter, ActionLogFilter)
from helixbilling.validator.validator import (ORDER_STATUS_UNKNOWN,
    ORDER_STATUS_LOCKED, ORDER_STATUS_CHARGED_OFF)
from helixcore.utils import filter_dict
from helixcore.actions.handler import detalize_error, AbstractHandler


def authentificate(method):
    @detalize_error(AuthError, RequestProcessingError.Category.auth, 'login')
    def decroated(self, data, curs):
        operator = self.get_operator(curs, data)
        data['operator_id'] = operator.id
        del data['login']
        del data['password']
        data.pop('custom_operator_info', None)
        return method(self, data, operator, curs)
    return decroated


class Handler(AbstractHandler):
    '''
    Handles all API actions. Method names are called like actions.
    '''
    def ping(self, data): #IGNORE:W0613
        return response_ok()

    def get_operator(self, curs, data):
        return selector.get_auth_opertator(curs, data['login'], data['password'])

    # --- currencies ---
    @transaction()
    def view_currencies(self, data, curs=None): #IGNORE:W0613
        ordering_params = data.get('ordering_params')
        currencies = selector.get_currencies(curs, ordering_params=ordering_params)
        def viewer(currency):
            return {
                'code': currency.code,
                'cent_factor': currency.cent_factor,
                'name': currency.name,
                'location': currency.location,
            }
        return response_ok(currencies=self.objects_info(currencies, viewer))

    # --- operator ---
    @transaction()
    @detalize_error(ObjectCreationError, RequestProcessingError.Category.data_integrity, 'login')
    def add_operator(self, data, curs=None):
        data['password'] = security.encrypt_password(data['password'])
        data.pop('custom_operator_info', None)
        try:
            mapping.insert(curs, Operator(**data))
        except ObjectCreationError:
            raise OperatorAlreadyExists(data['login'])
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(DataIntegrityError, RequestProcessingError.Category.data_integrity, 'new_login')
    def modify_operator(self, data, operator, curs=None):
        if 'new_password' in data:
            data['new_password'] = security.encrypt_password(data['new_password'])
        loader = partial(selector.get_operator, curs, operator.id, for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    # --- balance ---
    @transaction()
    @authentificate
    @detalize_error(CurrencyNotFound, RequestProcessingError.Category.data_integrity, 'currency')
    @detalize_error(ObjectCreationError, RequestProcessingError.Category.data_integrity, 'customer_id')
    def add_balance(self, data, operator, curs=None): #IGNORE:W0613
        currency = selector.get_currency_by_code(curs, data['currency'])
        data['currency_id'] = currency.id
        del data['currency']
        amount_fields = ['overdraft_limit']
        balance = Balance(**decimal_texts_to_cents(data, currency, amount_fields))
        mapping.insert(curs, balance)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def modify_balance(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)
        amount_fields = ['new_overdraft_limit']
        self.update_obj(curs, decimal_texts_to_cents(data, currency, amount_fields),
            partial(lambda x: x, balance))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def delete_balance(self, data, operator, curs=None):
        obj = selector.get_balance(curs, operator, data['customer_id'], for_update=True)
        mapping.delete(curs, obj)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def get_balance(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_balance(curs, operator, c_id)
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        return response_ok(**self.balance_viewer(currencies_idx, balance))

    def balance_viewer(self, currencies_idx, balance):
        currency = currencies_idx[balance.currency_id]
        return {
            'customer_id': balance.customer_id,
            'active': balance.active,
            'currency_code': currency.code,
            'creation_date': '%s' % balance.creation_date.isoformat(),
            'available_real_amount': '%s' % cents_to_decimal(currency, balance.available_real_amount),
            'available_virtual_amount': '%s' % cents_to_decimal(currency, balance.available_virtual_amount),
            'overdraft_limit': '%s' % cents_to_decimal(currency, balance.overdraft_limit),
            'locked_amount': '%s' % cents_to_decimal(currency, balance.locked_amount),
            'locking_order': balance.locking_order,
        }

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    def view_balances(self, data, operator, curs=None):
        f = BalanceFilter(operator, data['filter_params'], data['paging_params'],
            data.get('ordering_params'))
        balances, total = f.filter_counted(curs)
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        viewer = partial(self.balance_viewer, currencies_idx)
        return response_ok(balances=self.objects_info(balances, viewer), total=total)

    def check_amount_is_positive(self, data, f_name='amount'):
        val = Decimal(data[f_name])
        if val <= 0:
            raise ActionNotAllowedError("'%s' amount can't be processed" % val)

    def view_income_money(self, curs, data, operator, filter_cls):
        filter_params = data['filter_params']
        paging_params = data['paging_params']
        ordering_params = data.get('ordering_params')
        f = filter_cls(operator, filter_params, paging_params, ordering_params)
        objects, total = f.filter_counted(curs)

        filter_params = utils.filter_dict(('customer_ids', 'customer_id'), filter_params)
        balances = BalanceFilter(operator, filter_params, {}, None).filter_objs(curs)
        balances_c_id_idx = dict([(b.customer_id, b) for b in balances])
        currencies_idx = selector.get_currencies_indexed_by_id(curs)

        def viewer(obj):
            balance = balances_c_id_idx[obj.customer_id]
            currency = currencies_idx[balance.currency_id]
            return {
                'customer_id': obj.customer_id,
                'creation_date': obj.creation_date.isoformat(),
                'amount': '%s' % cents_to_decimal(currency, obj.amount),
                'currency': currency.code,
            }
        return (self.objects_info(objects, viewer), total)

    # --- receipt ---
    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(BalanceDisabled, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'amount')
    def enroll_receipt(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_active_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)

        amount_fields = ['amount']
        prep_data = decimal_texts_to_cents(data, currency, amount_fields)
        self.check_amount_is_positive(prep_data)
        receipt = Receipt(**prep_data)
        mapping.insert(curs, receipt)

        balance.available_real_amount += receipt.amount #IGNORE:E1101
        mapping.update(curs, balance)
        return response_ok()

    @transaction()
    @authentificate
    def view_receipts(self, data, operator, curs=None):
        receipts, total = self.view_income_money(curs, data, operator, ReceiptFilter)
        return response_ok(receipts=receipts, total=total)

    # --- bonus ---
    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(BalanceDisabled, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'amount')
    def enroll_bonus(self, data, operator, curs=None):
        c_id = data['customer_id']
        balance = selector.get_active_balance(curs, operator, c_id, for_update=True)
        currency = selector.get_currency_by_balance(curs, balance)

        amount_fields = ['amount']
        prep_data = decimal_texts_to_cents(data, currency, amount_fields)
        self.check_amount_is_positive(prep_data)
        bonus = Bonus(**prep_data)
        mapping.insert(curs, bonus)

        balance.available_virtual_amount += bonus.amount #IGNORE:E1101
        mapping.update(curs, balance)
        return response_ok()

    @transaction()
    @authentificate
    def view_bonuses(self, data, operator, curs=None):
        bonuses, total = self.view_income_money(curs, data, operator, BonusFilter)
        return response_ok(bonuses=bonuses, total=total)

    def _check_balances_are_active(self, balances):
        disabled_bss = filter(lambda x: x.active is False, balances)
        if disabled_bss:
            raise BalanceDisabled(', '.join([b.customer_id for b in disabled_bss]))

    # --- lock ---
    def _balance_lock(self, curs, operator, data_list):
        currencies_idx = selector.get_currencies_indexed_by_id(curs)
        c_ids = [d['customer_id'] for d in data_list]
        f = BalanceFilter(operator, {'customer_ids': c_ids}, {}, None)
        # ordering by id excepts deadlocks
        balances = f.filter_objs(curs, for_update=True)
        self._check_balances_are_active(balances)
        balances_idx = dict([(b.customer_id, b) for b in balances])
        customers_no_balance = set(c_ids) - set(balances_idx.keys())
        if customers_no_balance:
            raise BalanceNotFound(', '.join(customers_no_balance))

        for data in data_list:
            c_id = data['customer_id']
            balance = balances_idx[c_id]
            currency = currencies_idx[balance.currency_id]
            prep_data = decimal_texts_to_cents(data, currency, 'amount')
            self.check_amount_is_positive(prep_data)
            locks = compute_locks(currency, balance, prep_data['amount'])
            lock = BalanceLock(**{'operator_id': operator.id, 'customer_id': c_id,
                'order_id': data['order_id'],
                'order_type': data.get('order_type'),
                'real_amount': locks.get('available_real_amount', 0),
                'virtual_amount': locks.get('available_virtual_amount', 0),
            })
            mapping.insert(curs, lock)

            balance.available_real_amount -= lock.real_amount #IGNORE:E1101
            balance.available_virtual_amount -= lock.virtual_amount #IGNORE:E1101
            balance.locked_amount += lock.real_amount #IGNORE:E1101
            balance.locked_amount += lock.virtual_amount #IGNORE:E1101
            mapping.update(curs, balance)

    @transaction()
    @authentificate
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(BalanceDisabled, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ObjectCreationError, RequestProcessingError.Category.data_integrity, 'order_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'amount')
    def balance_lock(self, data, operator, curs=None):
        self._balance_lock(curs, operator, [data])
        return response_ok()

    @transaction()
    @authentificate
    def balance_lock_list(self, data, operator, curs=None):
        self._balance_lock(curs, operator, data['locks'])
        return response_ok()

    @transaction()
    @authentificate
    def view_balance_locks(self, data, operator, curs=None):
        filter_params = data['filter_params']
        paging_params = data['paging_params']
        ordering_params = data.get('ordering_params')

        f = BalanceLockFilter(operator, filter_params, paging_params, None)
        balance_locks, total = f.filter_counted(curs)

        filter_params = utils.filter_dict(('customer_ids', 'customer_id'), filter_params)
        balances = BalanceFilter(operator, filter_params, {}, ordering_params).filter_objs(curs)
        balances_c_id_idx = dict([(b.customer_id, b) for b in balances])
        currencies_idx = selector.get_currencies_indexed_by_id(curs)

        def viewer(balance_lock):
            balance = balances_c_id_idx[balance_lock.customer_id]
            currency = currencies_idx[balance.currency_id]
            return {
                'customer_id': balance_lock.customer_id,
                'order_id': balance_lock.order_id,
                'order_type': balance_lock.order_type,
                'real_amount': '%s' % cents_to_decimal(currency, balance_lock.real_amount),
                'virtual_amount': '%s' % cents_to_decimal(currency, balance_lock.virtual_amount),
                'currency': currency.code,
                'locking_date': balance_lock.locking_date.isoformat(),
            }
        return response_ok(balance_locks=self.objects_info(balance_locks, viewer), total=total)

    # --- unlock ---
    def _balance_unlock(self, curs, operator, data_list):
        c_ids = [d['customer_id'] for d in data_list]
        f = BalanceFilter(operator, {'customer_ids': c_ids}, {}, None)
        # ordering by id excepts deadlocks
        balances = f.filter_objs(curs, for_update=True)
        self._check_balances_are_active(balances)
        balances_idx = dict([(b.customer_id, b) for b in balances])
        customers_no_balance = set(c_ids) - set(balances_idx.keys())
        if customers_no_balance:
            raise BalanceNotFound(', '.join(customers_no_balance))

        for data in data_list:
            c_id = data['customer_id']
            ord_id = data['order_id']
            try:
                lock = selector.get_balance_lock(curs, operator, c_id, ord_id, for_update=True)
            except ObjectNotFound:
                raise ActionNotAllowedError(
                    'Cannot unlock money for customer %s order %s: '
                    'amount was not locked' % (c_id, ord_id)
                )
            mapping.delete(curs, lock)

            balance = balances_idx[lock.customer_id]
            balance.available_real_amount += lock.real_amount
            balance.available_virtual_amount += lock.virtual_amount
            balance.locked_amount -= lock.real_amount #IGNORE:E1101
            balance.locked_amount -= lock.virtual_amount #IGNORE:E1101
            mapping.update(curs, balance)

    @transaction()
    @authentificate
    @detalize_error(BalanceDisabled, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'order_id')
    def balance_unlock(self, data, operator, curs=None):
        self._balance_unlock(curs, operator, [data])
        return response_ok()

    @transaction()
    @authentificate
    def balance_unlock_list(self, data, operator, curs=None):
        self._balance_unlock(curs, operator, data['unlocks'])
        return response_ok()

    def _chargeoff(self, curs, operator, data_list):
        c_ids = [d['customer_id'] for d in data_list]
        f = BalanceFilter(operator, {'customer_ids': c_ids}, {}, None)
        # ordering by id excepts deadlocks
        balances = f.filter_objs(curs, for_update=True)
        self._check_balances_are_active(balances)
        balances_idx = dict([(b.customer_id, b) for b in balances])
        customers_no_balance = set(c_ids) - set(balances_idx.keys())
        if customers_no_balance:
            raise BalanceNotFound(', '.join(customers_no_balance))

        for data in data_list:
            c_id = data['customer_id']
            ord_id = data['order_id']
            try:
                lock = selector.get_balance_lock(curs, operator, c_id, ord_id, for_update=True)
            except ObjectNotFound:
                raise ActionNotAllowedError(
                    'Cannot charge off money for customer %s order %s: '
                    'amount was not locked'
                    % (c_id, ord_id)
                )

            chargeoff = ChargeOff(**{
                'operator_id': operator.id,
                'customer_id': lock.customer_id,
                'order_id': lock.order_id,
                'order_type': lock.order_type,
                'real_amount': lock.real_amount,
                'virtual_amount': lock.virtual_amount,
                'locking_date': lock.locking_date,
            })

            mapping.delete(curs, lock)
            mapping.insert(curs, chargeoff)

            balance = balances_idx[chargeoff.customer_id] #IGNORE:E1101
            balance.locked_amount -= chargeoff.real_amount #IGNORE:E1101
            balance.locked_amount -= chargeoff.virtual_amount #IGNORE:E1101

            mapping.update(curs, balance)

    @transaction()
    @authentificate
    @detalize_error(BalanceDisabled, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(BalanceNotFound, RequestProcessingError.Category.data_integrity, 'customer_id')
    @detalize_error(ActionNotAllowedError, RequestProcessingError.Category.data_integrity, 'order_id')
    def chargeoff(self, data, operator, curs=None):
        self._chargeoff(curs, operator, [data])
        return response_ok()

    @transaction()
    @authentificate
    def chargeoff_list(self, data, operator, curs=None):
        self._chargeoff(curs, operator, data['chargeoffs'])
        return response_ok()

    @transaction()
    @authentificate
    def view_chargeoffs(self, data, operator, curs=None):
        filter_params = data['filter_params']
        paging_params = data['paging_params']
        ordering_params = data.get('ordering_params')

        f = ChargeOffFilter(operator, filter_params, paging_params, ordering_params)
        chargeoffs, total = f.filter_counted(curs)

        filter_params = utils.filter_dict(('customer_ids', 'customer_id'), filter_params)
        balances = BalanceFilter(operator, filter_params, {}, None).filter_objs(curs)
        balances_c_id_idx = dict([(b.customer_id, b) for b in balances])
        currencies_idx = selector.get_currencies_indexed_by_id(curs)

        def viewer(chargeoff):
            balance = balances_c_id_idx[chargeoff.customer_id]
            currency = currencies_idx[balance.currency_id]
            return {
                'customer_id': chargeoff.customer_id,
                'order_id': chargeoff.order_id,
                'order_type': chargeoff.order_type,
                'real_amount': '%s' % cents_to_decimal(currency, chargeoff.real_amount),
                'virtual_amount': '%s' % cents_to_decimal(currency, chargeoff.virtual_amount),
                'currency': currency.code,
                'locking_date': chargeoff.locking_date.isoformat(),
                'chargeoff_date': chargeoff.chargeoff_date.isoformat(),
            }
        return response_ok(chargeoffs=self.objects_info(chargeoffs, viewer), total=total)

    @transaction()
    @authentificate
    def view_status(self, data, operator, curs=None):
        pass

    def order_statuses(self, curs, operator, filter_params, paging_params):
        bl_filter = BalanceLockFilter(operator, filter_params, paging_params, None)
        balance_locks = bl_filter.filter_objs(curs)
        bl_idx = dict([((bl.customer_id, bl.order_id), bl) for bl in balance_locks])

        ch_filter = ChargeOffFilter(operator, filter_params, paging_params, None)
        chargeoffs = ch_filter.filter_objs(curs)
        ch_idx = dict([((ch.customer_id, ch.order_id), ch) for ch in chargeoffs])

        c_ids = filter_params.get('customer_ids', [])
        if 'customer_id' in filter_params:
            c_ids.append(filter_params['customer_id'])
        order_ids = filter_params.get('order_ids', [])
        if 'order_id' in filter_params:
            order_ids.append(filter_params['order_id'])

        filter_params = utils.filter_dict(('customer_ids', 'customer_id'), filter_params)
        balances = BalanceFilter(operator, filter_params, {}, None).filter_objs(curs)
        balances_c_id_idx = dict([(b.customer_id, b) for b in balances])
        currencies_idx = selector.get_currencies_indexed_by_id(curs)

        statuses = []
        for c_id in c_ids:
            for order_id in order_ids:
                order_status = {
                    'customer_id': c_id,
                    'order_id': order_id,
                    'order_status': ORDER_STATUS_UNKNOWN,
                    'real_amount': None,
                    'virtual_amount': None,
                    'locking_date': None,
                    'chargeoff_date': None
                }
                k = (c_id, order_id)
                if k in bl_idx:
                    balance = balances_c_id_idx[c_id]
                    currency = currencies_idx[balance.currency_id]
                    balance_lock = bl_idx[k]
                    order_status['order_status'] = ORDER_STATUS_LOCKED
                    order_status['real_amount'] = '%s' % cents_to_decimal(currency, balance_lock.real_amount)
                    order_status['virtual_amount'] = '%s' % cents_to_decimal(currency, balance_lock.virtual_amount)
                    order_status['locking_date'] = balance_lock.locking_date.isoformat()
                if k in ch_idx:
                    balance = balances_c_id_idx[c_id]
                    currency = currencies_idx[balance.currency_id]
                    chargeoff = ch_idx[k]
                    order_status['order_status'] = ORDER_STATUS_CHARGED_OFF
                    order_status['real_amount'] = '%s' % cents_to_decimal(currency, chargeoff.real_amount)
                    order_status['virtual_amount'] = '%s' % cents_to_decimal(currency, chargeoff.virtual_amount)
                    order_status['locking_date'] = chargeoff.locking_date.isoformat()
                    order_status['chargeoff_date'] = chargeoff.chargeoff_date.isoformat()
                statuses.append(order_status)
        return statuses

    @transaction()
    @authentificate
    def order_status(self, data, operator, curs=None):
        filter_params = filter_dict(('customer_id', 'order_id'), data)
        statuses = self.order_statuses(curs, operator, filter_params, {})
        if len(statuses) > 1:
            raise SelectedMoreThanOneRow
        status = statuses[0]
        return response_ok(**status)

    @transaction()
    @authentificate
    def view_order_statuses(self, data, operator, curs=None):
        filter_params = data['filter_params']
        statuses = self.order_statuses(curs, operator, filter_params, {})
        return response_ok(order_statuses=statuses)

    @transaction()
    @authentificate
    def view_action_logs(self, data, operator, curs=None):
        filter_params = data['filter_params']
        paging_params = data['paging_params']
        ordering_params = data.get('ordering_params')

        f = ActionLogFilter(operator, filter_params, paging_params, ordering_params)
        action_logs, total = f.filter_counted(curs)

        def viewer(action_log):
            return {
                'custom_operator_info': action_log.custom_operator_info,
                'action': action_log.action,
                'customer_ids': action_log.customer_ids,
                'request_date': action_log.request_date.isoformat(),
                'remote_addr': action_log.remote_addr,
                'request': action_log.request,
                'response': action_log.response,
            }
        return response_ok(action_logs=self.objects_info(action_logs, viewer), total=total)
