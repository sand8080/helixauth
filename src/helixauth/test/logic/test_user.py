import unittest

from helixcore.error import RequestProcessingError

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import User, Service


class UserTestCase(ActorLogicTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.create_actor_env()

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
                self.assertEquals(sorted(['modify_user_self', 'get_user_rights', 'check_access']),
                    sorted(rights['properties']))


if __name__ == '__main__':
    unittest.main()