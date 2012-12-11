import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase


class CheckUserExistTestCase(ActorLogicTestCase):
    def setUp(self):
        super(CheckUserExistTestCase, self).setUp()
        self.create_actor_env()

    def test_check_access_user(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'id': 42424242}
        resp = self.check_user_exist(**req)
        self.check_response_ok(resp)
        self.assertFalse(resp['exist'])

        req = {'session_id': sess_id, 'email': 'u0@h.com', 'password': 'p'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        user_id = resp['id']
        req = {'session_id': sess_id, 'id': user_id}
        resp = self.check_user_exist(**req)
        self.check_response_ok(resp)
        self.assertTrue(resp['exist'])



if __name__ == '__main__':
    unittest.main()