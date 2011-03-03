from helixcore.test.util import ClientSimpleApplication

from helixauth.conf.log import logger
from helixauth.logic.actions import handle_action
from helixauth.wsgi.protocol import protocol
from helixauth.wsgi.server import HelixauthApplication


class Client(ClientSimpleApplication):
    def __init__(self):
        app = HelixauthApplication(handle_action, protocol, logger)
        super(Client, self).__init__(app)


def make_api_call(f_name):
    def m(self, **kwargs):
        kwargs['action'] = f_name
        return self.request(kwargs)
    m.__name__ = f_name #IGNORE:W0621
    return m


def get_api_calls():
    api_calls = [p.name for p in protocol]
    result = set()
    for api_call in api_calls:
        clean = api_call.replace('_request', '').replace('_response', '')
        result.add(clean)
    return result


for method_name in get_api_calls():
    setattr(Client, method_name, make_api_call(method_name))
