# coding=utf-8
import unittest

from helixcore.test.utils_for_testing import ActionsLogTester

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.test.wsgi.client import Client
from helixauth.db.dataobject import Service


class ActionLogTestCase(ActorLogicTestCase, ActionsLogTester):
    def setUp(self):
        super(ActionLogTestCase, self).setUp()
        self.cli = Client()
        req = {'name': self.actor_env_name,
            'su_email': self.actor_email, 'su_password': self.actor_password}
        self.cli.add_environment(**req)

    def login_actor(self):
        req = {'environment_name': self.actor_env_name,
            'email': self.actor_email, 'password': self.actor_password}
        resp = self.cli.login(**req)
        self.check_response_ok(resp)
        return resp['session_id']

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
            'email': 'l@h.com', 'password': 'fake'}
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
        l, p = 'l@h.com', 'p'
        req = {'session_id': sess_id, 'email': l, 'password': p}
        resp = self.cli.add_user(**req)
        self.check_response_ok(resp)

        req = {'environment_name': self.actor_env_name,
            'email': l, 'password': p}
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
        self._not_logged_action(action, sess_id, {})

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
        self._not_logged_filtering_action(action, sess_id)

    def test_delete_service(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'n', 'type': 't',
            'properties': ['a', 'b', 'c']}
        resp = self.cli.add_service(**req)
        self.check_response_ok(resp)
        srv_id = resp['id']

        action = 'delete_service'
        req = {'session_id': sess_id, 'id': srv_id}
        self._logged_action(action, req)

    def test_delete_unknown_service(self):
        sess_id = self.login_actor()
        action = 'delete_service'
        req = {'session_id': sess_id, 'id': 88888}
        self._logged_action(action, req, check_resp=False)

    def test_add_group(self):
        action = 'add_group'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'n',
            'rights': [{'service_id': 1, 'properties': ['a', 'b']}]}
        self._logged_action(action, req)

    def test_modify_group(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'n',
            'rights': [{'service_id': 1, 'properties': ['a', 'b']}]}
        resp = self.cli.add_group(**req)
        self.check_response_ok(resp)
        grp_id = resp['id']

        action = 'modify_group'
        req = {'session_id': sess_id, 'id': grp_id,
            'new_rights': [{'service_id': 1, 'properties': ['a']}]}
        self._logged_action(action, req)

    def test_delete_group(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'n',
            'rights': [{'service_id': 1, 'properties': ['a', 'b']}]}
        resp = self.cli.add_group(**req)
        self.check_response_ok(resp)
        grp_id = resp['id']

        action = 'delete_group'
        req = {'session_id': sess_id, 'id': grp_id}
        self._logged_action(action, req)

    def test_get_groups(self):
        action = 'get_groups'
        sess_id = self.login_actor()
        self._not_logged_filtering_action(action, sess_id)

    def _get_user_by_login(self, sess_id, email):
        req = {'session_id': sess_id, 'filter_params': {'email': email},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEquals(1, len(users))
        return users[0]

    def test_add_user(self):
        action = 'add_user'
        sess_id = self.login_actor()
        email = 'login@h.com'
        req = {'session_id': sess_id, 'email': email, 'password': 'p'}
        self._logged_action(action, req)

        # checking subject user ids are set
        user = self._get_user_by_login(sess_id, email)
        self._check_subject_users_ids_set(sess_id, action, user['id'])

    def test_get_users(self):
        action = 'get_users'
        sess_id = self.login_actor()
        self._not_logged_filtering_action(action, sess_id)

    def test_get_user_rights(self):
        action = 'get_user_rights'
        sess_id = self.login_actor()
        self._not_logged_action(action, sess_id, {})

    def test_modify_user_self(self):
        action = 'modify_user_self'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'old_password': self.actor_password,
            'new_password': 'p'}
        self._logged_action(action, req)

    def test_modify_users(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'email': 'u0@h.com', 'password': 'p'}
        resp = self.cli.add_user(**req)
        self.check_response_ok(resp)
        u_id = resp['id']

        action = 'modify_users'
        new_email = 'n_u0@h.com'
        req = {'session_id': sess_id, 'ids': [u_id],
            'new_email': new_email}
        self._logged_action(action, req)

        # checking subject user ids are set
        user = self._get_user_by_login(sess_id, new_email)
        self._check_subject_users_ids_set(sess_id, action, user['id'])

    def test_modify_users_failure_logged(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'paging_params': {},
            'filter_params': {'email': self.actor_email}}
        resp = self.cli.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEquals(1, len(users))
        u = users[0]

        u_id = u['id']
        action = 'modify_users'
        logs_num = self._count_self_records(sess_id, action)
        req = {'session_id': sess_id, 'ids': [u_id],
            'new_groups_ids': []}
        resp = self.cli.modify_users(**req)
        self.assertEquals('error', resp['status'])
        self.assertEquals(logs_num + 1,
            self._count_self_records(sess_id, action))
        self._check_subject_users_ids_set(sess_id, action, u_id)

    def test_get_action_logs(self):
        action = 'get_action_logs'
        sess_id = self.login_actor()
        self._not_logged_filtering_action(action, sess_id)

    def test_get_action_logs_self(self):
        action = 'get_action_logs_self'
        sess_id = self.login_actor()
        self._not_logged_filtering_action(action, sess_id)
        logins_num = self._count_self_records(sess_id, 'login')
        req = {'session_id': sess_id, 'email': 'l@h.com', 'password': 'p'}
        self._logged_action('add_user', req)
        req = {'environment_name': self.actor_env_name, 'email': 'l@h.com',
            'password': 'p'}
        resp = self.cli.login(**req)
        self.check_response_ok(resp)
        self.assertEquals(logins_num,
            self._count_self_records(sess_id, 'login'))

    def test_check_access(self):
        action = 'check_access'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        self._not_logged_action(action, sess_id, req)
        req = {'session_id': sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'fake'}
        self._not_logged_action(action, sess_id, req)
        req = {'session_id': sess_id, 'service_type': 'fake',
            'property': 'fake'}
        self._not_logged_action(action, sess_id, req)

    def test_check_user_exist(self):
        action = 'check_user_exist'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'id': 1}
        self._not_logged_action(action, sess_id, req)

    def test_get_notifications(self):
        action = 'get_notifications'
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'filter_params': {},
            'paging_params': {}, 'ordering_params': []}
        self._not_logged_action(action, sess_id, req)

    def test_modify_notifications(self):
        sess_id = self.login_actor()
        notifs = self.get_notifications_info(sess_id)
        notif = notifs[0]
        n_id = notif['id']

        action = 'modify_notifications'
        req = {'session_id': sess_id, 'ids': [n_id],
            'new_is_active': not notif['is_active']}
        self._logged_action(action, req)


if __name__ == '__main__':
    unittest.main()
