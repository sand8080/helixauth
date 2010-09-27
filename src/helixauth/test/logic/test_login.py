import unittest

from helixauth.test.service_test import ServiceTestCase


class LoginTestCase(ServiceTestCase):
    env_name = 'LoginTestCase'
    su_login = 'login_test_login'
    su_password = 'qweasdzxc'

    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.add_environment(self.env_name, self.su_login, self.su_password,
            'from %s' % self.env_name)

    def test_login_super_user(self):
        response = self.login(environment_name=self.env_name,
            login=self.su_login, password=self.su_password)
        self.assertEqual('ok', response['status'])
        self.get_session(response['session_id'])


if __name__ == '__main__':
    unittest.main()