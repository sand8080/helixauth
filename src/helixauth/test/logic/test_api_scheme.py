import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase


class ApiSchemeTestCase(ActorLogicTestCase):
    def setUp(self):
        super(ApiSchemeTestCase, self).setUp()
        self.create_actor_env()

    def test_get_scheme(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id}
        resp = self.get_api_scheme(**req)
        self.assertNotEquals(None, resp)



if __name__ == '__main__':
    unittest.main()