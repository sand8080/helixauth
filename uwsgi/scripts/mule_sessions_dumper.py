import datetime
from time import sleep
from functools import partial
import psycopg2
from psycopg2 import extensions
from psycopg2 import pool
extensions.register_type(psycopg2.extensions.UNICODE)

from helixcore import mapping
import helixcore.db.wrapper as wrapper

from helixauth.conf.log import sess_logger as logger
from helixauth.db.filters import SessionFilter
from helixauth.conf import settings
from helixauth.logic.session_utils import dump_into_db


cp = pool.SimpleConnectionPool(1, 2, user=settings.DSN['user'],
    database=settings.DSN['database'], host=settings.DSN['host'],
    password=settings.DSN['password'])
get_connection = cp.getconn
put_connection = cp.putconn

transaction = partial(wrapper.transaction, get_connection, put_connection)


def run():
    while True:
        dump_into_db(transaction)
        logger.debug('Sleeping %s minutes', settings.session_dump_to_db_minutes)
        sleep(settings.session_dump_to_db_minutes * 60)


if __name__=='__main__':
    logger.info('Sessions dumper started')
    run()
