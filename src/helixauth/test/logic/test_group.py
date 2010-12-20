import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase


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


if __name__ == '__main__':
    unittest.main()