import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import Notification


class NotificationsTestCase(ActorLogicTestCase):
    """
    default notifications created at environment creation step
    """
    def setUp(self):
        super(NotificationsTestCase, self).setUp()
        self.create_actor_env()

    def test_get_notifications(self):
        sess_id = self.login_actor()
        notifs = self.get_notifications_info(sess_id)
        self.assertTrue(len(notifs) > 0)

        notifs = self.get_notifications_info(sess_id,
            notif_type=Notification.TYPE_EMAIL)
        for n in notifs:
            self.assertEqual(Notification.TYPE_EMAIL, n['type'])

    def test_modify_notifications(self):
        sess_id = self.login_actor()
        notifs = self.get_notifications_info(sess_id)
        ids = [n['id'] for n in notifs]

        req = {'session_id': sess_id, 'ids': ids, 'new_is_active': False,
            'new_messages': []}
        resp = self.modify_notifications(**req)
        self.check_response_ok(resp)

        notifs = self.get_notifications_info(sess_id)
        for n_info in notifs:
            self.assertEquals(False, n_info['is_active'])
            self.assertEquals([], n_info['messages'])


if __name__ == '__main__':
    unittest.main()