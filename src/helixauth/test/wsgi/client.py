from helixcore.test.utils_for_testing import (ClientSimpleApplication, make_api_call,
    get_api_calls)

from helixauth.conf.log import logger
from helixauth.logic.actions import handle_action
from helixauth.wsgi.protocol import protocol
from helixauth.wsgi.application import HelixauthApplication


class Client(ClientSimpleApplication):
    def __init__(self):
        app = HelixauthApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app)


for method_name in get_api_calls(protocol):
    setattr(Client, method_name, make_api_call(method_name))
