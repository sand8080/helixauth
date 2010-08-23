from functools import partial

import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import helixauth.conf.lock_order #@UnusedImport IGNORE:W0611
import helixcore.db.wrapper as wrapper
from settings import DSN

from eventlet.db_pool import ConnectionPool
cp = ConnectionPool(psycopg2, user=DSN['user'], database=DSN['database'], host=DSN['host'], password=DSN['password'])
get_connection = cp.get
put_connection = cp.put

transaction = partial(wrapper.transaction, get_connection, put_connection)
