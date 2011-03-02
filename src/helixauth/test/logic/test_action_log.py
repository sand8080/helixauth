# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
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

    def _count_records(self, sess_id, action):
        req = {'session_id': sess_id, 'filter_params': {'action': action},
            'paging_params': {}, 'ordering_params': []}
        resp = self.get_action_logs(**req)
        self.check_response_ok(resp)
        return len(resp['action_logs'])

    def _logged_action(self, action, req):
        sess_id = req['session_id']
        logs_num = self._count_records(sess_id, action)
        api_call = getattr(self.cli, action)
        resp = api_call(**req)
        self.check_response_ok(resp)
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))

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

    def test_login_failed(self):
        action = 'login'
        sess_id = self.login_actor()
        req_al = {'session_id': sess_id, 'filter_params': {'action': action},
            'paging_params': {}, 'ordering_params': []}
        resp = self.get_action_logs(**req_al)
        self.check_response_ok(resp)
        logs_num = len(resp['action_logs'])

        req_login = {'environment_name': self.actor_env_name,
            'login': 'l', 'password': 'fake'}
        resp = self.cli.login(**req_login)
        self.assertEquals('error', resp['status'])
        resp = self.get_action_logs(**req_al)
        self.check_response_ok(resp)
        self.assertEquals(logs_num + 1, len(resp['action_logs']))

    def test_logout(self):
        action = 'logout'
        sess_id = self.login_actor()
        logs_num = self._count_records(sess_id, action)
        req = {'session_id': sess_id}
        self.cli.logout(**req)
        sess_id = self.login_actor()
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))
        # Logout with not existed session not logged
        self.cli.logout(**req)
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))

    def test_modify_environment(self):
        action = 'modify_environment'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'new_name': 'new_name'}
        self._logged_action(action, req)

    def test_modify_environment_failure(self):
        sess_id = self.login_actor()
        l, p = 'l', 'p'
        req = {'session_id': sess_id, 'login': l, 'password': p}
        resp = self.cli.add_user(**req)
        self.check_response_ok(resp)

        req = {'environment_name': self.actor_env_name,
            'login': l, 'password': p}
        resp = self.cli.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        action = 'modify_environment'
        logs_num = self._count_records(sess_id, action)
        req = {'session_id': u_sess_id, 'new_name': 'new_name'}
        resp = self.cli.modify_environment(**req)
        self.assertEquals('error', resp['status'])
        self.assertEquals(logs_num + 1, self._count_records(sess_id, action))

    def test_get_environment(self):
        action = 'get_environment'
        sess_id = self.login_actor()
        self.cli.get_environment()
        self.assertEquals(0, self._count_records(sess_id, action))

    def test_add_service(self):
        action = 'add_service'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'n', 'type': 't',
            'properties': ['a', 'b', 'c']}
        self._logged_action(action, req)

    def test_modify_service(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'n', 'type': 't',
            'properties': ['a', 'b', 'c']}
        resp = self.cli.add_service(**req)
        self.check_response_ok(resp)
        srv_id = resp['id']

        action = 'modify_service'
        req = {'session_id': sess_id, 'id': srv_id, 'new_name': 'lala',
            'new_is_active': False}
        self._logged_action(action, req)

    def test_get_services(self):
        action = 'get_services'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'filter_params': {},
            'paging_params': {}}
        resp = self.cli.get_services(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, self._count_records(sess_id, action))


if __name__ == '__main__':
    unittest.main()
