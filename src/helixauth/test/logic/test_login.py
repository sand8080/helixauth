import unittest

from helixcore.error import RequestProcessingError

from helixauth.test.logic.logic_test import LogicTestCase


class LoginTestCase(LogicTestCase):
    env_name = 'LoginTestCase'
    su_login = 'login_test_login'
    su_password = 'qweasdzxc'

    def setUp(self):
        super(LoginTestCase, self).setUp()
        req = {'name': self.env_name, 'su_login': self.su_login,
            'su_password': self.su_password,
            'custom_actor_info': 'from %s' % self.env_name}
        self.add_environment(**req)

    def test_login_super_user(self):
        resp = self.login(environment_name=self.env_name,
            login=self.su_login, password=self.su_password)
        self.check_response_ok(resp)
        self.get_session(resp['session_id'])

    def test_login_failed(self):
        # Wrong environment
        self.assertRaises(RequestProcessingError,
            self.login, environment_name='_%s_' % self.env_name,
            login=self.su_login, password=self.su_password)
        # Wrong login
        self.assertRaises(RequestProcessingError,
            self.login, environment_name=self.env_name,
            login='_%s_' % self.su_login, password=self.su_password)
        # Wrong password
        self.assertRaises(RequestProcessingError,
            self.login, environment_name=self.env_name,
            login=self.su_login, password='_%s_' % self.su_password)
        # User is inactive
        env = self.get_environment_by_name(self.env_name)
        user = self.get_subj_user(env.id, self.su_login, self.su_password)
        self.inactivate_user(user)
        self.assertRaises(RequestProcessingError,
            self.login, environment_name=self.env_name,
            login=self.su_login, password=self.su_password)


if __name__ == '__main__':
    unittest.main()