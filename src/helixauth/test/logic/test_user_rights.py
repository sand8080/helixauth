# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase


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
        req = {'session_id': session_id, 'name': 's0',
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


if __name__ == '__main__':
    unittest.main()