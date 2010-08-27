import unittest

#from helixcore.server.errors import RequestProcessingError
#from helixcore.misc.security import encrypt_password

from helixauth.test.service_test import ServiceTestCase


class EnvironmentTestCase(ServiceTestCase):
    def test_add_environment(self):
        pass


if __name__ == '__main__':
    unittest.main()