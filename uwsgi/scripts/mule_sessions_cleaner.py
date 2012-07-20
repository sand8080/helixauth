import datetime
from time import sleep

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.conf.log import sess_logger as logger
from helixauth.db.filters import SessionFilter


@transaction()
def clean(curs=None):
    to_d = datetime.datetime.now()
    logger.info('Sessions cleaning initiated %s', to_d)
    to_d = to_d - datetime.timedelta(minutes=settings.session_valid_minutes)
    logger.debug('Removing session older %s. Session valid period: %s minutes',
        to_d, settings.session_valid_minutes)
    f = SessionFilter({'to_update_date': to_d}, {}, None)
    sessions = f.filter_objs(curs)
    logger.info('Deleting %s sessions', len(sessions))
    mapping.delete_objects(curs, sessions)
    logger.info('Sessions cleaned')


def run():
    while True:
        clean()
        logger.debug('Sleeping %s minutes', settings.session_cleaning_minutes)
        sleep(settings.session_cleaning_minutes * 60)


if __name__=='__main__':
    logger.info('Sessions cleaner started')
    run()