import datetime
import unittest
import eventlet

from helixcore.test.util import profile

from helixauth.test.service_test import ServiceTestCase
from helixauth.test.wsgi.client import Client
from helixauth.wsgi.server import Server

eventlet.patcher.monkey_patch(all=False, socket=True)

eventlet.spawn(Server.run)


class ApplicationTestCase(ServiceTestCase):
    def setUp(self):
        super(ApplicationTestCase, self).setUp()
        self.cli = Client('%s' % datetime.datetime.now(), 'qazwsx')
        self.manager = self.cli

    def check_status_ok(self, result):
        self.assertEqual('ok', result['status'])

#    def test_invalid_request(self):
#        result = self.cli.request({'action': 'fakeaction'})
#        self.assertEqual('error', result['status'])
#        self.assertEqual('validation', result['category'])

    @profile
    def ping_loading(self, repeats=1): #IGNORE:W0613
        self.cli.ping() #IGNORE:E1101

    def test_ping(self):
        self.cli.ping()
        self.check_status_ok(self.cli.ping()) #IGNORE:E1101
        self.ping_loading(repeats=1)
        self.ping_loading(repeats=1000)

    @profile
    def get_api_actions_loading(self, repeats=1): #IGNORE:W0613
        self.cli.get_api_actions() #IGNORE:E1101

    def test_get_api_actions(self):
        self.cli.get_api_actions()
        self.get_api_actions_loading(repeats=1)
        self.get_api_actions_loading(repeats=1000)

    @profile
    def get_authorized_api_actions_loading(self, repeats=1): #IGNORE:W0613
        self.cli.get_authorized_api_actions() #IGNORE:E1101

    def test_get_authorized_api_actions(self):
        actions = self.cli.get_authorized_api_actions()
        for unauthorized in self.cli.unauthorized_commands:
            self.assertFalse(unauthorized in actions)
        self.get_authorized_api_actions_loading(repeats=1)
        self.get_authorized_api_actions_loading(repeats=1000)


if __name__ == '__main__':
    unittest.main()
