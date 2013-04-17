import unittest

from helixcore.error import RequestProcessingError

from helixauth.conf import settings
from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import User, Service


class UserTestCase(ActorLogicTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.create_actor_env()

    def test_add_user_by_super(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'email': 'user_1@h.com',
            'password': '1', 'role': User.ROLE_USER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess_id, 'email': 'user_2@h.com',
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
            'email': self.actor_login, 'password': new_pw}
        resp = self.login(**req)
        self.check_response_ok(resp)
        # checking password changed
        req = {'environment_name': self.actor_env_name,
            'email': self.actor_login, 'password': new_pw}
        resp = self.login(**req)
        self.check_response_ok(resp)

    def test_modify_user_self_empty_new_password(self):
        sess_id = self.login_actor()
        # checking empty password
        req = {'session_id': sess_id, 'old_password': self.actor_password,
            'new_password': ''}
        self.assertRaises(RequestProcessingError, self.modify_user_self, **req)

        # checking no password
        req = {'session_id': sess_id, 'old_password': self.actor_password}
        self.assertRaises(RequestProcessingError, self.modify_user_self, **req)

    def test_modify_user_self_new_lang(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'new_lang': User.LANG_EN}
        resp = self.modify_user_self(**req)
        self.check_response_ok(resp)
        user = self.get_user_info(sess_id, self.actor_login)
        self.assertEquals(User.LANG_EN, user['lang'])

        req = {'session_id': sess_id, 'new_lang': User.LANG_RU}
        resp = self.modify_user_self(**req)
        self.check_response_ok(resp)
        user = self.get_user_info(sess_id, self.actor_login)
        self.assertEquals(User.LANG_RU, user['lang'])

    def test_modify_super_users_failed(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'paging_params': {},
            'filter_params': {'email': self.actor_login}}
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
            req = {'session_id': sess_id, 'email': 'user_%s@h.com' % i,
                'password': 'p', 'role': User.ROLE_USER, 'groups_ids': []}
            resp = self.add_user(**req)
            self.check_response_ok(resp)
            u_ids.append(resp['id'])
        # trying to modify users
        req = {'session_id': sess_id, 'ids': u_ids, 'new_login': 'n_l'}
        self.assertRaises(RequestProcessingError, self.modify_users, **req)
        # checking modification canceled
        for i, u_id in enumerate(u_ids):
            users = self.get_users_info(sess_id, [u_id])
            u = users[0]
            self.assertEquals('user_%s@h.com' % i, u['email'])

    def test_deactivated_user_actions_denied(self):
        sess_id = self.login_actor()
        # adding user
        u0_email = 'u0@h.com'
        u0_password = 'p0'
        req = {'session_id': sess_id, 'email': u0_email,
            'password': u0_password, 'role': User.ROLE_USER,
            'groups_ids': []}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u0_id = resp['id']

        users = self.get_users_info(sess_id, [u0_id])
        self.assertEquals(1, len(users))
        u = users[0]
        self.assertEquals(u0_email, u['email'])
        self.assertEquals(True, u['is_active'])
        self.assertEquals([], u['groups_ids'])
        self.assertEquals(User.ROLE_USER, u['role'])

        # login user
        req = {'environment_name': self.actor_env_name,
            'email': u0_email, 'password': u0_password}
        resp = self.login(**req)
        self.check_response_ok(resp)
        s0_id = resp['session_id']
        # deactivating user
        req = {'session_id': sess_id, 'ids': [u0_id],
            'new_is_active': False}
        resp = self.modify_users(**req)
        self.check_response_ok(resp)
        # checking actions deprecated
        req = {'session_id': s0_id}
        self.assertRaises(RequestProcessingError, self.get_user_rights, **req)

    def test_modify_users(self):
        sess_id = self.login_actor()
        # adding user
        email = 'user_0@h.com'
        req = {'session_id': sess_id, 'email': email,
            'password': 'p', 'role': User.ROLE_USER, 'groups_ids': []}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u_id = resp['id']

        users = self.get_users_info(sess_id, [u_id])
        self.assertEquals(1, len(users))
        u = users[0]
        self.assertEquals(email, u['email'])
        self.assertEquals(True, u['is_active'])
        self.assertEquals([], u['groups_ids'])
        self.assertEquals(User.ROLE_USER, u['role'])
        self.assertEquals(User.DEFAULT_LANG, u['lang'])

        # adding group
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp_0',
            'rights': [{'service_id': 1, 'properties': ['one', 'two']}]
        }
        resp = self.add_group(**req)
        self.check_response_ok(resp)
        g_id = resp['id']

        # users modification
        new_email = 'n_l@h.com'
        new_lang = 'ru'
        req = {'session_id': sess_id, 'ids': [u_id], 'new_email': new_email,
            'new_password': 'n_p', 'new_is_active': False,
            'new_groups_ids': [g_id, 10000], 'new_lang': new_lang}
        resp = self.modify_users(**req)
        self.check_response_ok(resp)
        # checking modification
        users = self.get_users_info(sess_id, [u_id])
        self.assertEquals(1, len(users))
        u = users[0]
        self.assertEquals(new_email, u['email'])
        self.assertEquals(False, u['is_active'])
        self.assertEquals([g_id], u['groups_ids'])
        self.assertEquals(User.ROLE_USER, u['role'])
        self.assertEquals(new_lang, u['lang'])

    def test_get_users(self):
        # adding group
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp_0',
            'rights': [{'service_id': 1, 'properties': ['one', 'two']}]
        }
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        # adding users
        u0_email = 'user_0@h.com'
        req = {'session_id': sess_id, 'email': u0_email,
            'password': '1', 'role': User.ROLE_USER, 'groups_ids': [1]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u1_email = 'user_1@h.com'
        req['email'] = u1_email
        resp = self.add_user(**req)
        self.check_response_ok(resp)

        # checking filtering by login
        req = {'session_id': sess_id, 'filter_params': {'email': '*_1@h.com'},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(1, len(users))
        self.assertEqual(u1_email, users[0]['email'])

        # checking filtering by groups_ids
        req = {'session_id': sess_id, 'filter_params': {'groups_ids': [1, 2, 3]},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        users = resp['users']
        self.assertEqual(2, len(users))
        self.assertEqual(u0_email, users[0]['email'])
        self.assertEqual(u1_email, users[1]['email'])

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
        req = {'session_id': sess_id, 'email': 'user_1@h.com',
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
        req = {'session_id': sess_id, 'filter_params': {'email': self.actor_login},
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
        u0_email = 'u0@h.com'
        u0_pass = 'p0'
        req = {'session_id': sess_id, 'email': u0_email, 'password': u0_pass,
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)

        # login limited user
        req = {'environment_name': self.actor_env_name,
            'email': u0_email, 'password': u0_pass}
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

    def test_removed_group_user_not_in_groups_ids(self):
        sess_id = self.login_actor()
        grp_name = 'grp_0'
        req = {'session_id': sess_id, 'name': grp_name,
            'rights': [{'service_id': 1, 'properties': ['one', 'two']}]
        }
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'filter_params': {'name': grp_name},
            'paging_params': {}}
        resp = self.get_groups(**req)
        self.check_response_ok(resp)

        grps = resp['groups']
        self.assertEqual(1, len(grps))
        grp = grps[0]
        self.assertEqual(grp_name, grp['name'])

        # adding user
        req = {'session_id': sess_id, 'email': 'u0@h.com', 'password': 'p0',
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u_id = resp['id']

        # deleting group
        req = {'session_id': sess_id, 'id': grp['id']}
        resp = self.delete_group(**req)
        self.check_response_ok(resp)

        users = self.get_users_info(sess_id, [u_id])
        self.assertEquals(1, len(users))
        user = users[0]
        self.assertTrue(grp['id'] not in user['groups_ids'])


if __name__ == '__main__':
    unittest.main()