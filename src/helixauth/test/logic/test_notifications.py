import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import Notification
from helixauth.logic.notifier import Notifier
from helixauth.logic import message


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

    def test_reset_notifications(self):
        sess_id = self.login_actor()
        notifs = self.get_notifications_info(sess_id)
        ids = [n['id'] for n in notifs]

        req = {'session_id': sess_id, 'ids': ids,
            'new_messages': []}
        resp = self.modify_notifications(**req)
        self.check_response_ok(resp)
        notifs = self.get_notifications_info(sess_id)
        for n_info in notifs:
            self.assertEquals([], n_info['messages'])

        req = {'session_id': sess_id, 'ids': ids}
        resp = self.reset_notifications(**req)
        self.check_response_ok(resp)
        notifs = self.get_notifications_info(sess_id)
        n = Notifier()
        for n_info in notifs:
            self.assertNotEquals([], n_info['messages'])
            found = False
            for n_exp in n.default_email_notif_struct(n_info['event']):
                if n_exp in n_info['messages']:
                    found = True
                    break
            self.assertTrue(found)

    def test_load_new_notifications(self):
        e = 'TEST'
        setattr(message, 'EVENT_TEST', e)
        setattr(message, 'TEST_EMAIL_SUBJ_EN', 'subj')
        setattr(message, 'TEST_EMAIL_MSG_EN', 'msg')
        message.EVENTS_NAMES.append(e)
        message.EVENTS.append(e)

        sess_id = self.login_actor()
        notifs = self.get_notifications_info(sess_id)
        e_num_before = len(notifs)

        req = {'session_id': sess_id}
        resp = self.load_new_notifications(**req)
        self.check_response_ok(resp)

        notifs = self.get_notifications_info(sess_id)
        e_num_after = len(notifs)
        self.assertTrue(e_num_after > e_num_before)


if __name__ == '__main__':
    unittest.main()
