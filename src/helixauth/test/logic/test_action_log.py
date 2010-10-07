# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixauth.db.filters import ActionLogFilter
from helixauth.db.dataobject import User
from helixauth.conf.db import transaction
from helixauth.test.wsgi.client import Client


class ActionLogTestCase(ActorLogicTestCase):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client()
        req = {'name': self.actor_env_name,
            'su_login': self.actor_login, 'su_password': self.actor_password}
        self.cli.add_environment(**req)

    @transaction()
    def _check_action_tracked(self, environment, action, custom_actor_user_info, curs=None):
        filter_params = {'action': action, 'custom_actor_user_info': custom_actor_user_info}
        f = ActionLogFilter(environment.id, filter_params, {}, {})
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

    @transaction()
    def get_action_logs_num(self, environment, curs=None):
        f = ActionLogFilter(environment.id, {}, {}, {})
        return f.filter_objs_count(curs)

    def test_unauthorized_tracking_action(self):
        login = 'oper-action_log_test'
        name = 'action_logged'
        action = 'add_environment'
        self.cli.add_environment(name=name, su_login=login, su_password='qaz') #IGNORE:E1101
        environment = self.get_environment_by_name(name)
        self._check_action_tracked(environment, action, None)

    def test_tracking_error_action(self):
        environment = self.get_environment_by_name(self.actor_env_name)
        self.assertEquals(1, self.get_action_logs_num(environment))

        req = {'environment_name': self.actor_env_name, 'login': self.actor_login,
            'password': self.actor_password}
        self.cli.login(**req)
        self.assertEquals(2, self.get_action_logs_num(environment))

        req = {'environment_name': '_%s_' % self.actor_env_name,
            'login': self.actor_login, 'password': self.actor_password}
        self.cli.login(**req)

        # Environment is not defined so actions log by env is not changed
        self.assertEquals(2, self.get_action_logs_num(environment))
        class EnvImitator(object):
            id = None
        env_imitator = EnvImitator()
        self.assertEquals(1, self.get_action_logs_num(env_imitator))

    @transaction()
    def test_add_user(self, curs=None):
        resp = self.login_actor()
        self.check_response_ok(resp)
        session_id = resp['session_id']
        req = {'session_id': session_id, 'login': 'u0',
            'password': 'qazwsx', 'role': User.ROLE_SUPER}
        resp = self.cli.add_user(**req)
        self.check_response_ok(resp)

        env = self.get_environment_by_name(self.actor_env_name)
        self._check_action_tracked(env, 'add_user', None)
        subj_user = self.get_subj_user(env.id, 'u0', 'qazwsx')

        filter_params = {'action': 'add_user'}
        ordering_params = '-id'
        f = ActionLogFilter(env.id, filter_params, {}, ordering_params)
        a_logs = f.filter_objs(curs)
        a_l = a_logs[0]
        self.assertEqual([subj_user.id], a_l.subject_user_ids)


if __name__ == '__main__':
    unittest.main()
