import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import User


class UserTestCase(ActorLogicTestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()
        self.create_actor_env()

    def test_add_user_by_super(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'login': 'user_1',
            'password': '1', 'role': User.ROLE_SUPER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        req = {'session_id': sess_id, 'login': 'user_2',
            'password': '2', 'role': User.ROLE_USER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)

#    def test_modify_password(self):
#        pass


if __name__ == '__main__':
    unittest.main()