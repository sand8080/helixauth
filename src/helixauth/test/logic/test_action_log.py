# coding=utf-8
import unittest
import datetime

from helixauth.test.service_test import ServiceTestCase
from helixauth.test.wsgi.client import Client
from helixauth.conf.db import transaction
from helixauth.db.filters import ActionLogFilter


class ActionLogTestCase(ServiceTestCase):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client(u'авторизация %s' % datetime.datetime.now(), 'qazwsx')

    @transaction()
    def _check_action_tracked(self, environment, action, custom_actor_user_info, curs=None):
        filter_params = {'action': action, 'custom_actor_user_info': custom_actor_user_info}
        f = ActionLogFilter(environment, filter_params, {}, {})
        action_logs = f.filter_objs(curs)
        self.assertEqual(1, len(action_logs))
        action_log = action_logs[0]
        self.assertEqual(environment.id, action_log.environment_id)
        self.assertEqual(action, action_log.action)
        self.assertEqual(custom_actor_user_info, action_log.custom_actor_user_info)

    def _make_trackable_action(self, environment, action, data):
        self._make_action(action, data)
        self._check_action_tracked(environment, action, data.get('custom_operator_info'))

    def _make_action(self, action, data):
        auth_data = {'login': self.cli.login, 'password': self.cli.password}
        auth_data.update(data)
        m = getattr(self.cli, action)
        m(**auth_data)

    def test_unauthorized_tracking_action(self):
        login = 'oper-action_log_test'
        name = 'action_logged'
        action = 'add_environment'
        self.cli.add_environment(name=name, su_login=login, su_password='qaz') #IGNORE:E1101
        environment = self.get_environment_by_name(name)
        self._check_action_tracked(environment, action, None)

    @transaction()
    def get_action_logs_num(self, environment, curs=None):
        f = ActionLogFilter(environment, {}, {}, {})
        return f.filter_objs_count(curs)


    def test_tracking_error_action(self):
        name = 'action_logged'
        self.cli.add_environment(name=name, su_login=self.cli.login, su_password=self.cli.password) #IGNORE:E1101
        environment = self.get_environment_by_name(name)
        self.assertEquals(1, self.get_action_logs_num(environment))
        self.cli.add_environment(name=name, su_login=self.cli.login, su_password=self.cli.password) #IGNORE:E1101
        self.assertEquals(2, self.get_action_logs_num(environment))

#    def test_tracking_action(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#        operator = self.get_operator_by_login(self.cli.login)
#
#        self._make_trackable_action(operator, 'modify_operator', {'custom_operator_info': 'jah',
#            'new_password': self.cli.password})
#
#        c_id = 'tracked customer'
#        self._make_trackable_action(operator, 'add_balance', {'customer_id': c_id, 'active': True,
#            'currency': self.currency.code})
#        self._make_trackable_action(operator, 'modify_balance', {'customer_id': c_id, 'new_active': True})
#        self._make_trackable_action(operator, 'delete_balance', {'customer_id': c_id})
#        self._make_action('add_balance', {'customer_id': c_id, 'active': True,
#            'currency': self.currency.code})
#
#        self._make_trackable_action(operator, 'enroll_receipt', {'customer_id': c_id, 'amount': '15.00'})
#        self._make_trackable_action(operator, 'enroll_bonus', {'customer_id': c_id, 'amount': '25.00'})
#
#        order_id = 'lock_unlock'
#        self._make_trackable_action(operator, 'balance_lock', {'customer_id': c_id, 'order_id': order_id,
#            'amount': '20.00'})
#
#        self._make_trackable_action(operator, 'balance_unlock', {'customer_id': c_id, 'order_id': order_id})
#
#        order_id = 'lock_chargeoff'
#        self._make_action('balance_lock', {'customer_id': c_id, 'order_id': order_id, 'amount': '22.00'})
#        self._make_trackable_action(operator, 'chargeoff', {'customer_id': c_id, 'order_id': order_id})
#
#        c_id_1 = 'customer for list operations'
#        self._make_action('add_balance', {'customer_id': c_id_1, 'active': True,
#            'currency': self.currency.code})
#        self._make_action('enroll_receipt', {'customer_id': c_id_1, 'amount': '16.00'})
#        self._make_action('enroll_bonus', {'customer_id': c_id_1, 'amount': '26.00'})
#
#        order_id = 'lock_list_unlock_list'
#        self._make_trackable_action(operator, 'balance_lock_list', {'locks': [
#            {'customer_id': c_id, 'order_id': order_id, 'amount': '0.01'},
#            {'customer_id': c_id_1, 'order_id': order_id, 'order_type': 'ot', 'amount': '0.01'},
#        ]})
#        self._make_trackable_action(operator, 'balance_unlock_list', {'unlocks': [
#            {'customer_id': c_id, 'order_id': order_id},
#            {'customer_id': c_id_1, 'order_id': order_id},
#        ]})
#
#        order_id = 'lock_list_chargeoff_list'
#        self._make_action('balance_lock_list', {'locks': [
#            {'customer_id': c_id, 'order_id': order_id, 'amount': '0.01'},
#            {'customer_id': c_id_1, 'order_id': order_id, 'order_type': 'ot', 'amount': '0.01'},
#        ]})
#        self._make_action('chargeoff_list', {'chargeoffs': [
#            {'customer_id': c_id, 'order_id': order_id},
#            {'customer_id': c_id_1, 'order_id': order_id},
#        ]})
#
#    def test_view_action_logs(self):
#        self.cli.add_operator(login=self.cli.login, password=self.cli.password) #IGNORE:E1101
#        c_id_0 = 'view_action_logs_0'
#        c_id_1 = 'view_action_logs_1'
#        self._make_action('add_balance', {'customer_id': c_id_0, 'active': True, 'currency': self.currency.code})
#        self._make_action('add_balance', {'customer_id': c_id_1, 'active': True, 'currency': self.currency.code})
#        self._make_action('enroll_receipt', {'customer_id': c_id_0, 'amount': '15.00'})
#        self._make_action('enroll_bonus', {'customer_id': c_id_1, 'amount': '25.00'})
#        order_id_0 = '1'
#        self._make_action('balance_lock', {'customer_id': c_id_0, 'order_id': order_id_0, 'amount': '5.00'})
#        self._make_action('balance_lock', {'customer_id': c_id_1, 'order_id': order_id_0, 'amount': '6.00'})
#        order_id_1 = '2'
#        d_0 = datetime.datetime.now(pytz.utc)
#        self._make_action('balance_lock_list', {'locks': [
#            {'customer_id': c_id_0, 'order_id': order_id_1, 'amount': '7.00'},
#            {'customer_id': c_id_1, 'order_id': order_id_1, 'amount': '8.00'},
#        ]})
#        self._make_action('balance_unlock', {'customer_id': c_id_0, 'order_id': order_id_0})
#        self._make_action('balance_unlock_list', {'unlocks': [{'customer_id': c_id_1, 'order_id': order_id_0}]})
#
#        d_1 = datetime.datetime.now(pytz.utc)
#        self._make_action('chargeoff_list', {'chargeoffs': [{'customer_id': c_id_0, 'order_id': order_id_1},
#            {'customer_id': c_id_1, 'order_id': order_id_1},]})
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        self.assertEqual(11, response['total'])
#        self.assertEqual(11, len(response['action_logs']))
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'from_request_date': d_0.isoformat(), 'to_request_date': d_1.isoformat()},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        self.assertEqual(3, len(response['action_logs']))
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'action': 'balance_lock'},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        self.assertEqual(2, len(response['action_logs']))
#
#        data = {
#            'login': self.cli.login,
#            'password': self.cli.password,
#            'filter_params': {'customer_id': c_id_0},
#            'paging_params': {},
#        }
#        response = self.handle_action('view_action_logs', data)
#        al_info = response['action_logs']
#        self.assertEqual(6, len(al_info))
#        for al in al_info:
#            self.assertTrue(c_id_0 in al['customer_ids'])


if __name__ == '__main__':
    unittest.main()
