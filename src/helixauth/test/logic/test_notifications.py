import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import Notification


class NotificationsTestCase(ActorLogicTestCase):
    def setUp(self):
        super(NotificationsTestCase, self).setUp()
        self.create_actor_env()

    def test_get_notifications(self):
        # default notifications created at environment creation step
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'filter_params': {},
            'paging_params': {}}
        resp = self.get_notifications(**req)
        self.check_response_ok(resp)

        notifs = resp['notifications']
        self.assertTrue(len(notifs) > 0)

        req = {'session_id': sess_id, 'filter_params': {
            'type': Notification.TYPE_EMAIL},
            'paging_params': {}}
        resp = self.get_notifications(**req)
        self.check_response_ok(resp)
        notifs = resp['notifications']
        for n in notifs:
            self.assertEqual(Notification.TYPE_EMAIL, n['type'])


if __name__ == '__main__':
    unittest.main()