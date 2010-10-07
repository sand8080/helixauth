from helixcore.test.util import ClientSimpleApplication

from helixauth.conf.log import logger
from helixauth.logic.actions import handle_action
from helixauth.wsgi.protocol import protocol
from helixauth.wsgi.server import HelixauthApplication


class Client(ClientSimpleApplication):
    unauthorized_commands = ('ping', 'get_api_actions',
        'get_authorized_api_actions', 'add_environment')

    def __init__(self):
        app = HelixauthApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


methods = list(Client.unauthorized_commands +
    ('login', 'add_user', 'add_service'))

for method_name in methods:
    setattr(Client, method_name, make_api_call(method_name))
