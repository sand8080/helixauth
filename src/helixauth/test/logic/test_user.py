import unittest

from helixauth.test.service_test import ServiceTestCase
from helixauth.db.dataobject import User


class UserTestCase(ServiceTestCase):
    env_name = 'UserTestCase'
    su_login = 'su_test'
    su_password = 'qweasdzxc'

    def setUp(self):
        super(UserTestCase, self).setUp()
        req = {'name': self.env_name, 'su_login': self.su_login,
            'su_password': self.su_password,
            'custom_actor_info': 'from %s' % self.env_name}
        self.add_environment(**req)

    def test_add_user_by_super(self):
        resp = self.login(**{'environment_name': self.env_name, 'login': self.su_login,
            'password': self.su_password})
        self.check_response_ok(resp)
        session_id = resp['session_id']
        req = {'session_id': session_id, 'login': 'user_1',
            'password': '1', 'role': User.ROLE_SUPER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        req = {'session_id': session_id, 'login': 'user_2',
            'password': '2', 'role': User.ROLE_USER}
        resp = self.add_user(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()