DSN = {
    'user': '_DBC_DBUSER_',
    'database': '_DBC_DBNAME_',
    'host': '_DBC_DBSERVER_',
    'password': '_DBC_DBPASS_'
}


patch_table_name = 'patch'

server_host = 'localhost'
server_port = 9999
server_connections = 50

session_valid_minutes = 500

import logging
log_filename = '/var/log/helixproject/helixauth.log'
log_level = logging.DEBUG
log_format = "%(asctime)s [%(levelname)s] - %(message)s"
log_console = False
log_max_bytes = 2048000
log_backup_count = 20

import lock_order #IGNORE:W0611 @UnusedImport
