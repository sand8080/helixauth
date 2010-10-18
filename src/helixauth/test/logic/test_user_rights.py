# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.server.errors import RequestProcessingError


class UserRightsTestCase(ActorLogicTestCase):
    def setUp(self):
        super(UserRightsTestCase, self).setUp()
        self.create_actor_env()

    def test_modify_rights(self):
        session_id = self.login_actor()
        req = {'session_id': session_id, 'login': 'u0', 'password': 'p0'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u_id_0 = resp['user_id']

        ps = ['a', 'b', 'c', u'э', u'ю', u'я']
        req = {'session_id': session_id, 'name': 's0', 'type': 't',
            'properties': ps}
        resp = self.add_service(**req)
        s_id = resp['service_id']
        self.check_response_ok(resp)

        ps_0 = ps[2:]
        req = {'session_id': session_id, 'subject_users_ids': [u_id_0],
            'rights': [{'service_id': s_id, 'properties': ps_0}]}
        resp = self.modify_users_rights(**req)
        self.check_response_ok(resp)

        req = {'session_id': session_id, 'login': 'u1', 'password': 'p1'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u_id_1 = resp['user_id']

        ps_1 = ps[3:]
        req = {'session_id': session_id, 'subject_users_ids': [u_id_0, u_id_1],
            'rights': [{'service_id': s_id, 'properties': ps_1}]}
        resp = self.modify_users_rights(**req)
        self.check_response_ok(resp)

    def test_check_access_auth_srv(self):
        session_id = self.login_actor()
        req = {'session_id': session_id, 'login': 'u0', 'password': 'p0'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)

        # adding limited user
        u_id = resp['user_id']
        granted = ['add_user']
        env = self.get_environment_by_name(self.actor_env_name)
        srv = self.load_auth_service(env.id)
        req = {'session_id': session_id, 'subject_users_ids': [u_id],
            'rights': [{'service_id': srv.id, 'properties': granted}]}
        self.modify_users_rights(**req)

        # login limited user
        req = {'environment_name': env.name, 'login': 'u0', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        # checking access granted to service properties
        req = {'session_id': u_sess_id, 'login': 'u0-1', 'password': 'p0-1'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)

        # checking access denied to service properties
        req = {'session_id': u_sess_id, 'new_name': 'new env'}
        self.assertRaises(RequestProcessingError, self.modify_environment, **req)

        # check access with renamed auth sevice
        req = {'session_id': session_id, 'service_id': srv.id,
            'new_name': 'Bob'}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)

        req = {'session_id': u_sess_id, 'login': 'u0-2', 'password': 'p0-2'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()