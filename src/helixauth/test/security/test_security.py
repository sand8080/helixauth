import unittest

from helixauth.test.root_test import RootTestCase
from helixauth.security import sanitize_credentials, encrypt_passwords, PASSWORD_FIELDS


class SecurityTestCase(RootTestCase):
    def test_sanitize_credentials(self):
        d = {'login': 'l', 'password': 'p', 'new_password': 'np',
            'su_password': 'sp'}
        actual = sanitize_credentials(d)
        expected = {'login': 'l', 'password': '******',
            'new_password': '******', 'su_password': '******'}
        self.assertEqual(expected, actual)

    def test_encrypt_passwords(self):
        d = {'login': 'l', 'password': 'p', 'new_password': 'np',
            'su_password': 'sp'}
        enc_d = encrypt_passwords(d)
        for f in PASSWORD_FIELDS:
            self.assertNotEqual(d[f], enc_d[f])


if __name__ == '__main__':
    unittest.main()
