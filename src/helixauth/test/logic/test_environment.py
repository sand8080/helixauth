import unittest

from helixcore.error import RequestProcessingError

from helixauth.test.logic.logic_test import LogicTestCase


class EnvironmentTestCase(LogicTestCase):
    def test_add_environment(self):
        req = {'name': 'env_0', 'su_email': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)

        req['name'] = 'env_1'
        self.add_environment(**req)
        self.check_response_ok(resp)

    def test_add_environment_duplicate(self):
        req = {'name': 'env_0', 'su_email': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        self.add_environment(**req)
        req = {'name': 'env_0', 'su_email': 'b', 'su_password': 'a'}
        self.assertRaises(RequestProcessingError, self.add_environment,
            **req)

    def test_get_environment(self):
        name_0 = 'env_0'
        req = {'name': name_0, 'su_email': 'l@h.com', 'su_password': 'p'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)
        session_id = resp['session_id']

        resp = self.get_environment(**{'session_id': session_id})
        self.check_response_ok(resp)
        self.assertEquals({'id': 1, 'name': name_0}, resp['environment'])

    def test_modify_environment(self):
        req = {'name': 'env_0', 'su_email': 'su_env_login', 'su_password': 'qweasdzxc',
            'custom_actor_info': 'environment created from tests'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)
        session_id = resp['session_id']
        resp = self.modify_environment(**{'session_id': session_id,
            'new_name': 'modified_name_0'})
        self.check_response_ok(resp)
        resp = self.modify_environment(**{'session_id': session_id,
            'new_name': 'modified_name_1'})
        self.check_response_ok(resp)

    def test_name_duplication(self):
        name_0 = 'env_0'
        req = {'name': name_0, 'su_email': 'l@h.com', 'su_password': 'p'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)

        name_1 = 'env_1'
        req = {'name': name_1, 'su_email': 'l@h.com', 'su_password': 'p'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)

        session_id = resp['session_id']
        req = {'session_id': session_id, 'new_name': name_0}
        self.assertRaises(RequestProcessingError, self.modify_environment, **req)


if __name__ == '__main__':
    unittest.main()