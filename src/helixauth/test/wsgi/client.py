from helixcore.test.util import ClientApplication

from helixbilling.conf.log import logger
from helixbilling.logic.actions import handle_action
from helixbilling.validator.validator import protocol
from helixbilling.wsgi.server import HelixbillingApplication


class Client(ClientApplication):
    def __init__(self, login, password):
        app = HelixbillingApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app, login, password)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


for func_name in ['ping',
    'add_operator', 'modify_operator', 'delete_operator',
    'add_balance', 'modify_balance', 'delete_balance',
    'enroll_receipt', 'enroll_bonus',
    'balance_lock', 'balance_unlock', 'chargeoff',
    'balance_lock_list', 'balance_unlock_list', 'chargeoff_list',]:
    setattr(Client, func_name, make_api_call(func_name))
