import datetime
import cjson
import unittest
import eventlet

from helixcore.test.util import profile

from helixauth.test.service_test import ServiceTestCase
from helixauth.conf import settings
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

    @profile
    def ping_loading(self, repeats=1): #IGNORE:W0613
        self.cli.ping() #IGNORE:E1101

    def test_ping_ok(self):
        self.cli.ping()
        self.check_status_ok(self.cli.ping()) #IGNORE:E1101
        self.ping_loading(repeats=1)
        self.ping_loading(repeats=10000)

#    def test_invalid_request(self):
#        raw_result = self.cli.request({'action': 'fakeaction'})
#        result = cjson.decode(raw_result)
#        self.assertEqual('error', result['status'])
#        self.assertEqual('validation', result['category'])
#
#    def test_add_balance(self):
#        client_id = 'client id'
#        currency = self.get_currencies()[0]
#        self.cli.add_balance( #IGNORE:E1101
#            login=self.test_login,
#            password=self.test_password,
#            client_id=client_id,
#            active=True,
#            currency=currency.code,
#            overdraft_limit='100.00'
#        )


if __name__ == '__main__':
    unittest.main()
