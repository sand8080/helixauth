import unittest

from helixauth.test.root_test import RootTestCase
from helixauth.logic.auth import Authentifier


class AuthTestCase(RootTestCase):
    def test_salt(self):
        a = Authentifier()
        for _ in xrange(1000):
            s = a.salt()
            self.assertNotEquals(None, s)
            self.assertNotEquals('', s)


    def test_encrypt_password(self):
        a = Authentifier()
        p = a.encrypt_password('pass', 'salt')
        self.assertNotEquals(None, p)
        self.assertNotEquals('', p)

        enc_p1 = a.encrypt_password('1', '2')
        enc_p2 = a.encrypt_password('1', '2')
        self.assertEquals(enc_p1, enc_p2)


if __name__ == '__main__':
    unittest.main()