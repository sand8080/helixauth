import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError


class GroupTestCase(ActorLogicTestCase):
    def setUp(self):
        super(GroupTestCase, self).setUp()
        self.create_actor_env()

    def test_add_group(self):
        sess_id = self.login_actor()

        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        # Checking group (environment_id, name) is unique
        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 2, 'properties':['b']}]}
        self.assertRaises(RequestProcessingError, self.add_group, **req)

        req = {'name': 'env_1', 'su_login': 'l', 'su_password': 'p'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)

        # Checking name duplication is possible in different environments
        sess_id = resp['session_id']
        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 2, 'properties':['b']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()