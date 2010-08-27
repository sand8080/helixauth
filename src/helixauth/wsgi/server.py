#from helixauth.domain.objects import ActionLog
#from helixauth.logic import selector
#from helixcore import mapping
from eventlet import wsgi
from eventlet.green import socket

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.conf.log import logger
from helixauth.error import ObjectNotFound
from helixauth.logic.actions import handle_action
from helixauth.validator.validator import protocol
from helixcore.server.wsgi_application import Application
from helixcore.utils import filter_all_field_values


class HelixauthApplication(Application):
    def __init__(self, h, p, l):
        self.unauthorized_trackable = ['add_environment']
        super(HelixauthApplication, self).__init__(h, p, l, (
            'add_environment',
        ))

    @transaction()
    def track_api_call(self, remote_addr, s_req, s_resp, authorized_data, curs=None): #IGNORE:W0221
        super(HelixauthApplication, self).track_api_call(remote_addr, s_req, s_resp, authorized_data)
#        action_name = authorized_data['action']
#        user_id = None
#        if action_name in self.unauthorized_trackable:
#            try:
#                login = authorized_data['login']
##                user_id = selector.get_operator_by_login(curs, login).id
#            except ObjectNotFound:
#                self.logger.log(logging.ERROR,
#                    'Unable to track action for not existed operator. Request: %s. Response: %s', (s_req, s_resp))
#        else:
#            user_id = authorized_data['operator_id']
#        c_ids = list(filter_all_field_values('customer_id', authorized_data))
#        data = {
#            'operator_id': user_id,
#            'custom_operator_info': authorized_data.get('custom_operator_info', None),
#            'customer_ids': c_ids,
#            'action': action_name,
#            'remote_addr': remote_addr,
#            'request': s_req,
#            'response': s_resp,
#        }
#        mapping.insert(curs, ActionLog(**data))


class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.log(l, 'server: %s' % s)

    @staticmethod
    def run():
        sock = socket.socket()
        sock.bind((settings.server_host, settings.server_port))
        sock.listen(settings.server_connections)
        wsgi.server(
            sock,
            HelixauthApplication(handle_action, protocol, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
