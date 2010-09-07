from eventlet import wsgi
from eventlet.green import socket

from helixauth.conf import settings
from helixauth.conf.log import logger
from helixauth.logic.actions import handle_action
from helixauth.wsgi.application import HelixauthApplication
from helixauth.wsgi.protocol import protocol


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
