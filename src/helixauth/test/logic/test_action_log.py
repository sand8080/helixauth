# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixauth.db.filters import ActionLogFilter
from helixauth.conf.db import transaction
from helixauth.test.wsgi.client import Client


class ActionLogTestCase(ActorLogicTestCase):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client()
        req = {'name': self.actor_env_name,
            'su_login': self.actor_login, 'su_password': self.actor_password}
        self.cli.add_environment(**req)

    def login_actor(self):
        req = {'environment_name': self.actor_env_name,
            'login': self.actor_login, 'password': self.actor_password}
        resp = self.cli.login(**req)
        self.check_response_ok(resp)
        return resp['session_id']

#    def test_tracking_duplicate_environment(self):
#        environment = self.get_environment_by_name(self.actor_env_name)
#        self.assertEquals(1, self.get_action_logs_num(environment))
#        req = {'name': self.actor_env_name, 'su_login': 'l',
#            'su_password': 'p'}
#        self.cli.add_environment(**req)
#        class EnvEmulator(object):
#            id = None
#        self.assertEquals(1, self.get_action_logs_num(EnvEmulator()))
#
#    @transaction()
#    def test_add_user(self, curs=None):
#        session_id = self.login_actor()
#        req = {'session_id': session_id, 'login': 'u0',
#            'password': 'qazwsx'}
#        resp = self.cli.add_user(**req)
#        self.check_response_ok(resp)
#
#        env = self.get_environment_by_name(self.actor_env_name)
#        self._check_action_tracked(env, 'add_user', None)
#        subj_user = self.get_subj_user(env.id, 'u0', 'qazwsx')
#
#        filter_params = {'action': 'add_user'}
#        ordering_params = '-id'
#        f = ActionLogFilter(env.id, filter_params, {}, ordering_params)
#        a_logs = f.filter_objs(curs)
#        a_l = a_logs[0]
#        self.assertEqual([subj_user.id], a_l.subject_users_ids)
#
#    @transaction()
#    def test_add_service(self, curs=None):
#        session_id = self.login_actor()
#        req = {'session_id': session_id, 'name': u'сервис', 'type': 'type',
#            'properties': list('qazwsx'), 'is_active': False}
#        resp = self.cli.add_service(**req)
#        self.check_response_ok(resp)
#
#        env = self.get_environment_by_name(self.actor_env_name)
#        self._check_action_tracked(env, 'add_service', None)

#    def test_get_action_logs(self):
#        sess_id = self.login_actor()
#        req = {'session_id': sess_id, 'filter_params': {},
#            'paging_params': {}, 'ordering_params': []}
#        resp = self.get_action_logs(**req)
#        self.check_response_ok(resp)

    def _count_records(self, sess_id, action):
        req = {'session_id': sess_id, 'filter_params': {'action': action},
            'paging_params': {}, 'ordering_params': []}
        resp = self.get_action_logs(**req)
        self.check_response_ok(resp)
        return len(resp['action_logs'])

    def test_login(self):
        action = 'login'
        sess_id = self.login_actor()
        logs_num = self._count_records(sess_id, action)

        self.login_actor()
        req = {'session_id': sess_id, 'filter_params': {'action': action},
            'paging_params': {}, 'ordering_params': []}
        resp = self.get_action_logs(**req)
        self.check_response_ok(resp)
        for a_l in resp['action_logs']:
            self.assertNotEquals(None, a_l['session_id'])
            self.assertEquals('login', a_l['action'])
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))

    def test_logout(self):
        action = 'logout'
        sess_id = self.login_actor()
        logs_num = self._count_records(sess_id, action)

        self.cli.logout(**{'session_id': sess_id})
        sess_id = self.login_actor()
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))

    def test_add_environment(self):
        action = 'add_environment'
        sess_id = self.login_actor()
        self.assertEquals(1, self._count_records(sess_id, action))

    def test_get_environment(self):
        action = 'get_environment'
        sess_id = self.login_actor()
        self.cli.get_environment()
        self.assertEquals(0, self._count_records(sess_id, action))

#    def test_tracking_error_action(self):
#        environment = self.get_environment_by_name(self.actor_env_name)
#        self.assertEquals(1, self.get_action_logs_num(environment))
#
#        req = {'environment_name': self.actor_env_name, 'login': self.actor_login,
#            'password': self.actor_password}
#        self.cli.login(**req)
#        self.assertEquals(2, self.get_action_logs_num(environment))
#
#        req = {'environment_name': '_%s_' % self.actor_env_name,
#            'login': self.actor_login, 'password': self.actor_password}
#        self.cli.login(**req)
#
#        # Environment is not defined so actions log by env is not changed
#        self.assertEquals(2, self.get_action_logs_num(environment))
#        class EnvImitator(object):
#            id = None
#        env_imitator = EnvImitator()
#        self.assertEquals(1, self.get_action_logs_num(env_imitator))


if __name__ == '__main__':
    unittest.main()
