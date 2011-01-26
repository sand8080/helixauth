import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError


class LogoutTestCase(ActorLogicTestCase):
    def test_logout(self):
        self.create_actor_env()
        sess_id = self.login_actor()
        req = {'session_id': sess_id}
        resp = self.logout(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess_id}
        self.assertRaises(RequestProcessingError, self.logout, **req)


if __name__ == '__main__':
    unittest.main()