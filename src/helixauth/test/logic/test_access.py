import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import Service
from helixcore.error import RequestProcessingError


class AccessTestCase(ActorLogicTestCase):
    def test_check_access_super_user(self):
        self.create_actor_env()
        sess_id = self.login_actor()
        req = { 'session_id': sess_id, 'property': 'check_access',
            'service_type': Service.TYPE_AUTH}
        resp = self.check_access(**req)
        self.check_response_ok(resp)
        env_id = resp['environment_id']
        user_id = resp['user_id']

        req = {'session_id': sess_id}
        resp = self.get_environment(**req)
        self.check_response_ok(resp)
        env = resp['environment']
        self.assertEquals(env_id, env['id'])

        req = {'session_id': sess_id, 'filter_params': {'login': self.actor_login},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        user = resp['users'][0]
        self.assertEquals(user_id, user['id'])

        # checking fake property access denied
        req = { 'session_id': sess_id, 'property': 'fake',
            'service_type': Service.TYPE_AUTH}
        self.assertRaises(RequestProcessingError, self.check_access, **req)
        # checking fake service access denied
        req = { 'session_id': sess_id, 'property': 'check_access',
            'service_type': 'fake_service'}
        self.assertRaises(RequestProcessingError, self.check_access, **req)

    def test_access_limited_user(self):
        self.create_actor_env()
        sess_id = self.login_actor()

        # creating another service
        req = {'session_id': sess_id, 'name': 's1', 'type': 'ts1',
            'properties': ['a', 'b']}
        resp = self.add_service(**req)
        self.check_response_ok(resp)

        # adding limited user
        req = {'session_id': sess_id, 'filter_params': {'name': 'Users'},
            'paging_params': {}}
        resp = self.get_groups(**req)
        self.check_response_ok(resp)
        groups = resp['groups']
        self.assertEqual(1, len(groups))
        grp = groups[0]

        req = {'session_id': sess_id, 'login': 'u0', 'password': 'p0',
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        env = self.get_environment_by_name(self.actor_env_name)

        # login limited user
        req = {'environment_name': env.name, 'login': 'u0', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        # checking access granted to service properties
        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        resp = self.check_access(**req)
        self.check_response_ok(resp)

        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'add_user'}
        self.assertRaises(RequestProcessingError, self.check_access, **req)

    def test_access_denied_when_group_inactive(self):
        self.create_actor_env()
        sess_id = self.login_actor()

        # adding limited user
        req = {'session_id': sess_id, 'filter_params': {'name': 'Users'},
            'paging_params': {}}
        resp = self.get_groups(**req)
        self.check_response_ok(resp)
        groups = resp['groups']
        self.assertEqual(1, len(groups))
        grp = groups[0]
        self.assertEqual(True, grp['is_active'])

        req = {'session_id': sess_id, 'login': 'u0', 'password': 'p0',
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        env = self.get_environment_by_name(self.actor_env_name)

        # login limited user
        req = {'environment_name': env.name, 'login': 'u0', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        # checking access granted to service properties
        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        resp = self.check_access(**req)
        self.check_response_ok(resp)

        # inactivating group
        req = {'session_id': sess_id, 'id': grp['id'], 'new_is_active': False}
        resp = self.modify_group(**req)
        self.check_response_ok(resp)

        # checking access denied to service properties (in new session)
        req = {'environment_name': env.name, 'login': 'u0', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        self.assertRaises(RequestProcessingError, self.check_access, **req)


if __name__ == '__main__':
    unittest.main()