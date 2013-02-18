import unittest

from helixauth.test.root_test import RootTestCase
from helixauth.logic.notifier import Notifier


class AccessTestCase(RootTestCase):
    def test_default_register_user_notif(self):
        n = Notifier()
        msg = n.default_register_user_notif(None)
        self.assertNotEquals(None, msg['en'])
        self.assertNotEquals(None, msg['en']['email_subj'])
        self.assertNotEquals(None, msg['en']['email_msg'])
        self.assertNotEquals(None, msg['ru'])
        self.assertNotEquals(None, msg['ru']['email_subj'])
        self.assertNotEquals(None, msg['ru']['email_msg'])


if __name__ == '__main__':
    unittest.main()