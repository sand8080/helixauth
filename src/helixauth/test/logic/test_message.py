import unittest

from helixauth.test.root_test import RootTestCase
from helixauth.logic import message as m


class MessageTestCase(RootTestCase):
    def test_events(self):
        self.assertTrue(len(m.EVENTS) > 0)
        for e in m.EVENTS:
            self.assertTrue(e.startswith('EVENT_'))


if __name__ == '__main__':
    unittest.main()