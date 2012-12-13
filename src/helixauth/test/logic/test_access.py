import json
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixcore.error import RequestProcessingError
from helixcore import mapping

from helixauth.conf.db import transaction
from helixauth.db.dataobject import Service
from helixauth.db.filters import SessionFilter


class AccessTestCase(ActorLogicTestCase):
    def _check_access(self, resp, value):
        self.check_response_ok(resp)
        self.assertEquals(value, resp['access'])

    def check_access_granted(self, resp):
        self._check_access(resp, 'granted')

    def check_access_denied(self, resp):
        self._check_access(resp, 'denied')

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

        req = {'session_id': sess_id, 'filter_params': {'email': self.actor_login},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        user = resp['users'][0]
        self.assertEquals(user_id, user['id'])

        # checking fake property access denied
        req = { 'session_id': sess_id, 'property': 'fake',
            'service_type': Service.TYPE_AUTH}
        resp = self.check_access(**req)
        self.check_access_denied(resp)

        # checking fake service access denied
        req = { 'session_id': sess_id, 'property': 'check_access',
            'service_type': 'fake_service'}
        resp = self.check_access(**req)
        self.check_access_denied(resp)

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

        req = {'session_id': sess_id, 'email': 'u0@h.com', 'password': 'p0',
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        env = self.get_environment_by_name(self.actor_env_name)

        # login limited user
        req = {'environment_name': env.name, 'email': 'u0@h.com', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        # checking access granted to service properties
        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        resp = self.check_access(**req)
        self.check_access_granted(resp)

        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'add_user'}
        resp = self.check_access(**req)
        self.check_access_denied(resp)

    def test_not_logged_user(self):
        self.create_actor_env()
        req = {'session_id': 'fake_session', 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
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

        req = {'session_id': sess_id, 'email': 'u0@h.com', 'password': 'p0',
            'groups_ids': [grp['id']]}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        env = self.get_environment_by_name(self.actor_env_name)

        # login limited user
        req = {'environment_name': env.name, 'email': 'u0@h.com', 'password': 'p0'}
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
        req = {'environment_name': env.name, 'email': 'u0@h.com', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        self.assertRaises(RequestProcessingError, self.check_access, **req)

    def test_access_granted_binded_to_ip(self):
        self.create_actor_env()
        sess_id = self.login_actor(bind_to_ip=True)

        # checking access granted to service properties
        req = {'session_id': sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        resp = self.check_access(**req)
        self.check_response_ok(resp)

    @transaction()
    def _change_session_ip(self, sess_id, curs=None):
        # changing ip in session
        f = SessionFilter({'session_id': sess_id}, {}, None)
        s = f.filter_one_obj(curs)
        data = json.loads(s.serialized_data)
        data['ip'] = 'new_%s' % data['ip']
        s.serialized_data = json.dumps(data)
        mapping.save(curs, s)

    def test_access_denied_binded_to_ip(self):
        self.create_actor_env()
        sess_id = self.login_actor(bind_to_ip=True)

        # checking access granted to service properties
        req = {'session_id': sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        resp = self.check_access(**req)
        self.check_response_ok(resp)

        self._change_session_ip(sess_id)

        req = {'session_id': sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        self.assertRaises(RequestProcessingError, self.check_access, **req)


if __name__ == '__main__':
    unittest.main()