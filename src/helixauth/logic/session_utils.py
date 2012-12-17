import datetime
import memcache

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.log import sess_logger as logger
from helixauth.db.filters import SessionFilter
from helixauth.error import SessionNotFound


def clean(trn_wrapper):
    @trn_wrapper()
    def _clean(curs=None):
        to_d = datetime.datetime.now()
        logger.info("Sessions cleaning initiated %s", to_d)
        to_d = to_d - datetime.timedelta(minutes=settings.session_valid_minutes)
        logger.debug("Removing session older %s. Session valid period: %s minutes",
            to_d, settings.session_valid_minutes)
        f = SessionFilter({'to_update_date': to_d}, {}, ['id'])
        sessions = f.filter_objs(curs)
        logger.info("Deleting %s sessions", len(sessions))
        mapping.delete_objects(curs, sessions)
        logger.info("Sessions cleaned")
    _clean()


def dump_into_db(trn_wrapper):
    if not settings.session_caching_enabled:
        logger.debug("Sessions caching disabled. Nothing to dump")
        return

    sessions = _get_sessions()

    mem_cache = memcache.Client([settings.session_memcached_addr])
    logger.info("Dumping %s sessions into db", len(sessions))
    for s in sessions:
        _dump_session(mem_cache, s)
    logger.info("Sessions dumping complete")

    @trn_wrapper()
    def _get_sessions(curs=None):
        from_d = datetime.datetime.now()
        logger.info("Sessions dumping into db initiated %s", from_d)
        from_d = from_d - datetime.timedelta(minutes=settings.session_valid_minutes)
        logger.debug("Fetching not expired sessions, newer %s. Session valid period: %s minutes",
            from_d, settings.session_valid_minutes)
        f = SessionFilter({'from_update_date': from_d}, {}, ['id'])
        return f.filter_objs(curs)

    @trn_wrapper()
    def _dump_session(mem_cache, session, curs=None):
        f = SessionFilter({'id': session.id}, {}, None)
        try:
            s = f.filter_one_obj(curs, for_update=True)
            sess_id = s.session_id.encode('utf8')
            cached_s = mem_cache.get(sess_id)
            if cached_s is None:
                logger.debug("Session %s not found in cache", sess_id)
            else:
                if cached_s.update_date > s.update_date:
                    s.update_date = cached_s.update_date
                    mapping.save(curs, s)
                    logger.debug("Session %s dumped from cache into db", sess_id)
                else:
                    logger.debug("Session %s update_date in db greater than in cache. " \
                        "Noting to dump", sess_id)
        except SessionNotFound, e:
            logger.error("Dumping session failed: %s", e)

