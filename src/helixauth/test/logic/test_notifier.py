import unittest

from helixauth.test.root_test import RootTestCase
from helixauth.logic.notifier import Notifier


class AccessTestCase(RootTestCase):
    def test_default_register_user_notif(self):
        n = Notifier()
        msgs = n.default_register_user_notif(None)
        self.assertEquals(2, len(msgs))
        msg = msgs[0]
        self.assertTrue('lang' in msg)
        self.assertTrue('email_subj' in msg)
        self.assertTrue('email_msg' in msg)

    def test_register_user(self):
        n = Notifier()
        n_process = n.register_user()
        self.assertEquals(False, n_process['is_sent'])


if __name__ == '__main__':
    unittest.main()