import unittest

from helixcore.server.errors import RequestProcessingError

from helixauth.test.service_test import ServiceTestCase


class EnvironmentTestCase(ServiceTestCase):
    def test_add_environment(self):
        name = 'env_0'
        su_login = 'su_env_login'
        su_password = 'qweasdzxc'
        custom_user_info = 'environment created from tests'
        self.add_environment(name, su_login, su_password, custom_user_info)

#    def test_add_environment_duplicate(self):
#        name = 'env_0'
#        su_login = 'su_env_login'
#        su_password = 'qweasdzxc'
#        self.add_environment(name, su_login, su_password)
#        self.assertRaises(RequestProcessingError, self.add_environment,
#            name,'a', 'b', 'c')

#    def test_modify_environment(self):
#        name = 'env_0'
#        su_login = 'su_env_login'
#        su_password = 'qweasdzxc'
#        custom_user_info = 'environment created from tests'
#        resp = self.add_environment(name, su_login, su_password, custom_user_info)
#        session_id = resp.get('session_id')
#        self.modify_environment(**{'session_id': session_id, 'name': name,
#            'new_name': '%s_modified_by_session' % name})

if __name__ == '__main__':
    unittest.main()