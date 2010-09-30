import unittest

from helixcore.server.errors import RequestProcessingError

from helixauth.test.service_test import ServiceTestCase
from helixauth.conf.db import transaction


class EnvironmentTestCase(ServiceTestCase):
    def test_add_environment(self):
        req = {'name': 'env_0', 'su_login': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        self.add_environment(**req)

    def test_add_environment_duplicate(self):
        req = {'name': 'env_0', 'su_login': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        self.add_environment(**req)
        req = {'name': 'env_0', 'su_login': 'b', 'su_password': 'a'}
        self.assertRaises(RequestProcessingError, self.add_environment,
            **req)

    def test_modify_environment(self):
        req = {'name': 'env_0', 'su_login': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        response = self.add_environment(**req)
        session_id = response['session_id']
        response = self.modify_environment(**{'session_id': session_id,
            'new_name': 'modified_name'})

    @transaction()
    def test_modify_failure(self, curs=None):
        req = {'name': 'env_0', 'su_login': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        response = self.add_environment(**req)
        session_id = response['session_id']
        self.assertRaises(RequestProcessingError, self.modify_environment,
            session_id='%s_modified' % session_id, new_name='nn_0')
        self.make_session_expired(session_id)
        self.assertRaises(RequestProcessingError, self.modify_environment,
            session_id=session_id, new_name='nn_1')


if __name__ == '__main__':
    unittest.main()