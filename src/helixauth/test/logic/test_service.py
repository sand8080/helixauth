# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase


class ServiceTestCase(ActorLogicTestCase):
    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.create_actor_env()

    def test_add_service(self):
        resp = self.login_actor()
        self.check_response_ok(resp)
        session_id = resp['session_id']

        req = {'session_id': session_id, 'name': u'сервис0',
            'properties': ['alpha', u'бетта']}
        resp = self.add_service(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()