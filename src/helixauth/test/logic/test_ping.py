import unittest

from helixauth.test.logic.logic_test import LogicTestCase


class PingTestCase(LogicTestCase):
    def test_ping(self):
        self.ping(**{})


if __name__ == '__main__':
    unittest.main()