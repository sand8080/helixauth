from functools import partial

import psycopg2
from psycopg2 import extensions
from psycopg2 import pool
extensions.register_type(psycopg2.extensions.UNICODE)

import helixauth.conf.lock_order #@UnusedImport IGNORE:W0611
import helixcore.db.wrapper as wrapper
from settings import DSN


cp = pool.SimpleConnectionPool(1, 10, user=DSN['user'], database=DSN['database'], host=DSN['host'], password=DSN['password'])
get_connection = cp.getconn
put_connection = cp.putconn

transaction = partial(wrapper.transaction, get_connection, put_connection)
