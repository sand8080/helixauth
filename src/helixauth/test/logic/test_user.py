import unittest

from helixcore.error import RequestProcessingError

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

    def test_modify_password(self):
        sess_id = self.login_actor()
        # checking is impossible to change password with wrong old password
        req = {'session_id': sess_id, 'old_password': 'fake%s' % self.actor_password,
            'new_password': 'lala'}
        self.assertRaises(RequestProcessingError, self.modify_password, **req)
        # changing password
        new_pw = 'new%s' % self.actor_password
        req = {'session_id': sess_id, 'old_password': self.actor_password,
            'new_password': new_pw}
        resp = self.modify_password(**req)
        self.check_response_ok(resp)
        # checking password changed
        req = {'environment_name': self.actor_env_name,
            'login': self.actor_login, 'password': new_pw}
        resp = self.login(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()