import unittest

from helixcore.error import RequestProcessingError

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import User, Service


class UserTestCase(ActorLogicTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.create_actor_env()

    def _get_users(self, sess_id, ids):
        req = {'session_id': sess_id, 'filter_params': {'ids': ids},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        return resp['users']

    def test_add_user_by_super(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'login': 'user_1',
            'password': '1', 'role': User.ROLE_USER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess_id, 'login': 'user_2',
            'password': '2', 'role': User.ROLE_USER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)

    def test_modify_user_self(self):
        sess_id = self.login_actor()
        # checking is impossible to change password with wrong old password
        req = {'session_id': sess_id, 'old_password': 'fake%s' % self.actor_password,
            'new_password': 'lala'}
        self.assertRaises(RequestProcessingError, self.modify_user_self, **req)
        # changing password
        new_pw = 'new%s' % self.actor_password
        req = {'session_id': sess_id, 'old_password': self.actor_password,
            'new_password': new_pw}
        resp = self.modify_user_self(**req)
        self.check_response_ok(resp)
        # checking password changed
        req = {'environment_name': self.actor_env_name,
            'login': self.actor_login, 'password': new_pw}
        resp = self.login(**req)
        self.check_response_ok(resp)

    def test_modify_super_users_failed(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'paging_params': {},
            'filter_params': {'login': self.actor_login}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(1, len(users))
        su_id = users[0]['id']
        req = {'session_id': sess_id, 'subject_users_ids': [su_id]}
        self.assertRaises(RequestProcessingError, self.modify_users, **req)

    def test_modify_users_login_failed(self):
        sess_id = self.login_actor()
        # adding users
        u_ids = []
        for i in range(2):
            req = {'session_id': sess_id, 'login': 'user_%s' % i,
                'password': 'p', 'role': User.ROLE_USER, 'groups_ids': []}
            resp = self.add_user(**req)
            self.check_response_ok(resp)
            u_ids.append(resp['id'])
        # trying to modify users
        req = {'session_id': sess_id, 'ids': u_ids, 'new_login': 'n_l'}
        self.assertRaises(RequestProcessingError, self.modify_users, **req)
        # checking modification canceled
        for i, u_id in enumerate(u_ids):
            users = self._get_users(sess_id, [u_id])
            u = users[0]
            self.assertEquals('user_%s' % i, u['login'])

    def test_modify_users(self):
        sess_id = self.login_actor()
        # adding user
        req = {'session_id': sess_id, 'login': 'user_0',
            'password': 'p', 'role': User.ROLE_USER, 'groups_ids': []}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u_id = resp['id']

        users = self._get_users(sess_id, [u_id])
        self.assertEquals(1, len(users))
        u = users[0]
        self.assertEquals('user_0', u['login'])
        self.assertEquals(True, u['is_active'])
        self.assertEquals([], u['groups_ids'])
        self.assertEquals(User.ROLE_USER, u['role'])

        # adding group
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp_0',
            'rights': [{'service_id': 1, 'properties': ['one', 'two']}]
        }
        resp = self.add_group(**req)
        self.check_response_ok(resp)
        g_id = resp['id']

        # users modification
        req = {'session_id': sess_id, 'ids': [u_id], 'new_login': 'n_l',
            'new_password': 'n_p', 'new_is_active': False,
            'new_groups_ids': [g_id, 10000]}
        resp = self.modify_users(**req)
        self.check_response_ok(resp)
        # checking modification
        users = self._get_users(sess_id, [u_id])
        self.assertEquals(1, len(users))
        u = users[0]
        self.assertEquals('n_l', u['login'])
        self.assertEquals(False, u['is_active'])
        self.assertEquals([g_id], u['groups_ids'])
        self.assertEquals(User.ROLE_USER, u['role'])

    def test_get_users(self):
        # adding group
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp_0',
            'rights': [{'service_id': 1, 'properties': ['one', 'two']}]
        }
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        # adding users
        req = {'session_id': sess_id, 'login': 'user_0',
            'password': '1', 'role': User.ROLE_USER, 'groups_ids': [1]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        req['login'] = 'user_1'
        resp = self.add_user(**req)
        self.check_response_ok(resp)

        # checking filtering by login
        req = {'session_id': sess_id, 'filter_params': {'login': '*_1'},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(1, len(users))
        self.assertEqual('user_1', users[0]['login'])

        # checking filtering by groups_ids
        req = {'session_id': sess_id, 'filter_params': {'groups_ids': [1, 2, 3]},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(2, len(users))
        self.assertEqual('user_0', users[0]['login'])
        self.assertEqual('user_1', users[1]['login'])

        # checking filtering by roles
        req = {'session_id': sess_id, 'filter_params': {'roles': [User.ROLE_SUPER]},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(1, len(users))
        self.assertEqual(User.ROLE_SUPER, users[0]['role'])

        # checking filtering without params
        req = {'session_id': sess_id, 'filter_params': {},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(3, len(users))

    def test_add_user_with_groups(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp_0',
            'rights': [{'service_id': 1, 'properties': ['one', 'two']}]
        }
        resp = self.add_group(**req)

        # checking only existed groups ids used for user
        self.check_response_ok(resp)
        req = {'session_id': sess_id, 'login': 'user_1',
            'password': '1', 'role': User.ROLE_USER, 'groups_ids': [1, 7, 9]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        user_id = resp['id']

        req = {'session_id': sess_id, 'filter_params': {'ids': [user_id]},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(1, len(users))
        user = users[0]
        self.assertEqual([1], user['groups_ids'])

        # checking groups ids ignored for super user
        req = {'session_id': sess_id, 'filter_params': {'login': self.actor_login},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(1, len(users))
        user = users[0]
        self.assertEqual([], user['groups_ids'])

    def test_get_user_rights(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id}
        resp = self.get_user_rights(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'filter_params': {'name': 'Users'},
            'paging_params': {}}
        resp = self.get_groups(**req)
        self.check_response_ok(resp)
        groups = resp['groups']
        self.assertEqual(1, len(groups))
        grp = groups[0]

        # adding limited user
        req = {'session_id': sess_id, 'login': 'u0', 'password': 'p0',
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)

        # login limited user
        req = {'environment_name': self.actor_env_name,
            'login': 'u0', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        s0_id = resp['session_id']
        req = {'session_id': s0_id}
        resp = self.get_user_rights(**req)
        self.check_response_ok(resp)
        rights_l = resp['rights']
        for rights in rights_l:
            if rights['service_type'] == Service.TYPE_AUTH:
                self.assertEquals(sorted(['modify_user_self', 'get_user_rights',
                    'get_action_logs_self', 'check_access']),
                    sorted(rights['properties']))


if __name__ == '__main__':
    unittest.main()