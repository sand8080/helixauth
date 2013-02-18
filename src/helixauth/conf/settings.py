DSN = {
    'user': 'helixauth',
    'database': 'helixauth',
    'host': 'localhost',
    'password': 'gbd0hs,fr0k,fcf'
}


patch_table_name = 'patch'

session_valid_minutes = 60
session_cleaning_minutes = 5
session_caching_enabled = True
session_memcached_addr = '127.0.0.1:11211'
session_dump_to_db_minutes = 5
session_max_fixed_lifetime_minutes = 120

import logging
log_filename = '/opt/helixproject/helixauth/helixauth/log/helixauth.log'
sess_log_filename = '/opt/helixproject/helixauth/helixauth/log/helixauth-sess.log'
log_level = logging.DEBUG
log_format = "%(asctime)s [%(levelname)s] - %(message)s"
log_console = False
log_max_bytes = 2048000
log_backup_count = 20

import lock_order #IGNORE:W0611 @UnusedImport

default_messages_lang = 'en'
notifications_enabled = False
