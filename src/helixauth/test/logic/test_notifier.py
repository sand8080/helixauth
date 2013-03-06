import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.dataobject import Notification
from helixauth.logic import message
from helixauth.logic.notifier import Notifier, NotificationProcessing


class NotifierTestCase(ActorLogicTestCase):
    def setUp(self):
        super(NotifierTestCase, self).setUp()
        self.create_actor_env()

    def test_prepare_notif_emailing_disabled(self):
        env = self.get_environment_by_name(self.actor_env_name)
        n = Notifier()
        s_old = settings.email_notifications_enabled
        settings.email_notifications_enabled = False
        try:
            n_proc = n._prepare_notif(env.id, message.EVENT_REGISTER_USER,
                Notification.TYPE_EMAIL, message.LANG_EN, None)
            n_proc_info = n_proc.to_dict()
            self.assertEquals(False, n_proc_info['is_sent'])
            self.assertEquals({}, n_proc_info['message_data'])
            self.assertEquals(
                [NotificationProcessing.STEP_NOTIFECATIONS_DISABLED],
                n_proc_info['processing_steps'])
        except Exception, e:
            raise e
        finally:
            settings.email_notifications_enabled = s_old

    @transaction()
    def test_prepare_notif_unknown_event(self, curs=None):
        env = self.get_environment_by_name(self.actor_env_name)
        n = Notifier()
        s_old = settings.email_notifications_enabled
        settings.email_notifications_enabled = True
        try:
            n_proc = n._prepare_notif(env.id, 'FAKE',
                Notification.TYPE_EMAIL, message.LANG_EN, curs)
            n_proc_info = n_proc.to_dict()
            self.assertEquals(False, n_proc_info['is_sent'])
            self.assertEquals({}, n_proc_info['message_data'])
            self.assertEquals(
                [NotificationProcessing.STEP_NOTIFECATIONS_ENABLED,
                NotificationProcessing.STEP_UNKNOWN_EVENT],
                n_proc_info['processing_steps'])
        except Exception, e:
            raise e
        finally:
            settings.email_notifications_enabled = s_old

    @transaction()
    def test_prepare_notif_disabled(self, curs=None):
        sess_id = self.login_actor()
        ns_info = self.get_notifications_info(sess_id)
        n_info = ns_info[0]
        n_id = n_info['id']
        req = {'session_id': sess_id, 'ids': [n_id],
            'new_is_active': False}
        resp = self.modify_notifications(**req)
        self.check_response_ok(resp)

        env = self.get_environment_by_name(self.actor_env_name)
        n = Notifier()
        s_old = settings.email_notifications_enabled
        settings.email_notifications_enabled = True
        try:
            n_proc = n._prepare_notif(env.id, message.EVENT_REGISTER_USER,
                Notification.TYPE_EMAIL, message.LANG_EN, curs)
            n_proc_info = n_proc.to_dict()
            self.assertEquals(False, n_proc_info['is_sent'])
            self.assertEquals({}, n_proc_info['message_data'])
            self.assertEquals(
                [NotificationProcessing.STEP_NOTIFECATIONS_ENABLED,
                NotificationProcessing.STEP_EVENT_NOTIFICATION_DISABLED],
                n_proc_info['processing_steps'])
        except Exception, e:
            raise e
        finally:
            settings.email_notifications_enabled = s_old

    @transaction()
    def test_prepare_notif_default_lang_selection(self, curs=None):
        env = self.get_environment_by_name(self.actor_env_name)
        n = Notifier()
        s_old = settings.email_notifications_enabled
        settings.email_notifications_enabled = True
        try:
            n_proc = n._prepare_notif(env.id, message.EVENT_REGISTER_USER,
                Notification.TYPE_EMAIL, 'FAKE', curs)
            n_proc_info = n_proc.to_dict()
            self.assertEquals(False, n_proc_info['is_sent'])
            self.assertEquals(
                [NotificationProcessing.STEP_NOTIFECATIONS_ENABLED,
                NotificationProcessing.STEP_EVENT_NOTIFICATION_ENABLED,
                NotificationProcessing.STEP_MSG_LANG_NOT_FOUND,
                NotificationProcessing.STEP_MSG_DFLT_LANG_FOUND],
                n_proc_info['processing_steps'])
        except Exception, e:
            raise e
        finally:
            settings.email_notifications_enabled = s_old


if __name__ == '__main__':
    unittest.main()