from eventlet import wsgi, spawn
from eventlet.green import socket

from helixauth.conf import settings
from helixauth.conf.log import logger
from helixauth.logic.actions import handle_action
from helixauth.wsgi.application import HelixauthApplication
from helixauth.wsgi.protocol import protocol
from helixauth.logic import session_cleaner


class Server(object):
    class ServerLog(object):
        def write(self, s, l=0): #IGNORE:W0613
            logger.log(l, 'server: %s' % s)

    @staticmethod
    def run():
        spawn(session_cleaner.run)
        sock = socket.socket() #@UndefinedVariable
        sock.bind((settings.server_host, settings.server_port))
        sock.listen(settings.server_connections)
        logger.debug('Auth service started on %s:%s',
            settings.server_host, settings.server_port)
        wsgi.server(
            sock,
            HelixauthApplication(handle_action, protocol, logger),
            max_size=5000,
            log=Server.ServerLog()
        )
