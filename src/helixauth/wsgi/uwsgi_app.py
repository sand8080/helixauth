from helixauth.conf.log import logger
from helixauth.logic.actions import handle_action
from helixauth.wsgi.protocol import protocol
from helixauth.wsgi.application import HelixauthApplication


application = HelixauthApplication(handle_action, protocol, logger)
