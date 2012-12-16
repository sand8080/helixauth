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
from helixauth.logic.session_utils import clean


cp = pool.SimpleConnectionPool(1, 2, user=settings.DSN['user'],
    database=settings.DSN['database'], host=settings.DSN['host'],
    password=settings.DSN['password'])
get_connection = cp.getconn
put_connection = cp.putconn

transaction = partial(wrapper.transaction, get_connection, put_connection)


@transaction()
def _clean(curs=None):
    """
    function for transaction wrapping
    """
    clean(curs)


def run():
    while True:
        _clean()
        logger.debug('Sleeping %s minutes', settings.session_cleaning_minutes)
        sleep(settings.session_cleaning_minutes * 60)


if __name__=='__main__':
    logger.info('Sessions cleaner started')
    run()
