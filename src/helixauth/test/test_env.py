import os
import logging

from helixauth.conf import settings


settings.DSN = {
    'user': 'helixtest',
    'database': 'test_helixauth',
    'host': 'localhost',
    'password': 'qazwsx'
}

settings.log_filename = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    '..', '..', '..', 'log', 'helixauth_test.log')
settings.sess_log_filename = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    '..', '..', '..', 'log', 'helixauth-sess_test.log')
settings.log_level = logging.DEBUG
settings.log_console = True

settings.session_valid_minutes = 500
settings.session_cleaning_minutes = 1
settings.session_caching_enabled = True
settings.session_dump_to_db_minutes = 1

patches_path = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    '..', '..', 'patches')


settings.email_notifications_enabled = False
