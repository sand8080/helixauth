import unittest

from helixcore.server.errors import RequestProcessingError

from helixauth.test.service_test import ServiceTestCase
from helixauth.error import UserNotFound


class LoginTestCase(ServiceTestCase):
    env_name = 'LoginTestCase'
    su_login = 'login_test_login'
    su_password = 'qweasdzxc'

    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.add_environment(self.env_name, self.su_login, self.su_password,
            'from %s' % self.env_name)
#        self.env = self.get_environment_by_name(self.env_name)

    def test_login_super_user(self):
        response = self.login(environment_name=self.env_name,
            login=self.su_login, password=self.su_password)
#        raise UserNotFound(a='1', b=2, c=3)
#        session = self.get_session(response['session_id'])


if __name__ == '__main__':
    unittest.main()