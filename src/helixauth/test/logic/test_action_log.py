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
        self.cli = Client()

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
        su_login = 'su_login_%s' % datetime.datetime.now()
        su_password = 'qazwsx'
        self.cli.add_environment(name=name, su_login=su_login, su_password=su_password) #IGNORE:E1101
        environment = self.get_environment_by_name(name)
        self.assertEquals(1, self.get_action_logs_num(environment))

        self.cli.login(environment_name=name, login='_%s_' % su_login, password=su_password) #IGNORE:E1101
        self.assertEquals(2, self.get_action_logs_num(environment))

        self.cli.login(environment_name='_%s_' % name, login=su_login, password=su_password) #IGNORE:E1101
        # Environment is not defined so actions log by env is not changed
        self.assertEquals(2, self.get_action_logs_num(environment))
        class EnvImitator(object):
            id = None
        env_imitator = EnvImitator()
        self.assertEquals(1, self.get_action_logs_num(env_imitator))


if __name__ == '__main__':
    unittest.main()
