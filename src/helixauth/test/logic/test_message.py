import unittest

from helixauth.test.root_test import RootTestCase
from helixauth.logic import message as m


class MessageTestCase(RootTestCase):
    def test_events_names(self):
        self.assertTrue(len(m.EVENTS) > 0)
        # Checking in events values, not names
        for e in m.EVENTS_NAMES:
            self.assertTrue(e.startswith('EVENT_'))

    def test_events(self):
        self.assertTrue(len(m.EVENTS) > 0)
        # Checking in events values, not names
        for e in m.EVENTS:
            self.assertFalse(e.startswith('EVENT_'))


if __name__ == '__main__':
    unittest.main()