from helixauth.conf import settings
import os

settings.DSN = {
    'user': 'helixtest',
    'database': 'test_helixauth',
    'host': 'localhost',
    'password': 'qazwsx'
}

settings.server_host = 'localhost'
settings.server_port = 10999

import logging
settings.log_filename = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'helixauth.log')
settings.log_level = logging.DEBUG
#settings.log_level = logging.ERROR
settings.log_console = True

patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..', '..', 'patches')
