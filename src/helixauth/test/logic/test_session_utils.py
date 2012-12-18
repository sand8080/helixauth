import unittest
from time import sleep
import memcache

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixauth.conf import settings
from helixauth.error import SessionNotFound
from helixauth.logic.session_utils import dump_into_db
from helixcore import mapping
origin_sess_valid_minutes = settings.session_valid_minutes

from helixauth.conf.db import transaction
from helixauth.db.filters import SessionFilter
from helixauth.logic import session_utils


class SessionUtilsTestCase(ActorLogicTestCase):
    def setUp(self):
        super(SessionUtilsTestCase, self).setUp()
        self.mem_cache = memcache.Client([settings.session_memcached_addr])
        settings.session_valid_minutes = 0.01

    def tearDown(self):
        settings.session_valid_minutes = origin_sess_valid_minutes
        super(SessionUtilsTestCase, self).tearDown()

    def test_clean(self, curs=None):
        self.create_actor_env()
        sess_id = self.login_actor()
        self.get_session(sess_id)
        sleep(settings.session_valid_minutes * 60)
        session_utils.clean(transaction)
        self.assertRaises(SessionNotFound, self.get_session, sess_id)

    def test_session_cache_expiration(self):
        settings.session_valid_minutes = 1.0 / 60
        self.create_actor_env()
        sess_id = self.login_actor()
        str_sess_id = sess_id.encode('utf8')
        sleep(settings.session_valid_minutes * 60 * 1)
        self.assertEquals(None, self.mem_cache.get(str_sess_id))

    def test_session_caching(self):
        settings.session_valid_minutes = 1
        self.create_actor_env()
        sess_id = self.login_actor()
        str_sess_id = sess_id.encode('utf8')
        self.assertNotEquals(None, self.mem_cache.get(str_sess_id))

    def test_dump_into_db(self):
        settings.session_valid_minutes = 1
        self.create_actor_env()
        sess_id = self.login_actor()
        sess_db = self.get_session(sess_id)
        # updating session in cache by making request
        sleep(1)
        req = {'session_id': sess_id}
        resp = self.get_api_scheme(**req)
        self.check_response_ok(resp)
        # checking update_date difference between cached and stored sessions
        sess_cache = self.mem_cache.get(sess_id.encode('utf8'))
        self.assertTrue(sess_cache.update_date > sess_db.update_date)
        # checking update_date equal in cached and stored sessions
        dump_into_db(transaction)
        sess_db = self.get_session(sess_id)
        self.assertEquals(sess_cache.update_date, sess_db.update_date)

    @transaction()
    def _remove_session(self, sess_id, curs=None):
        f = SessionFilter({'session_id': sess_id}, {}, None)
        sess = f.filter_one_obj(curs)
        mapping.delete(curs, sess)

    def test_dump_removed_session(self):
        settings.session_valid_minutes = 1.0 / 60
        self.create_actor_env()
        sess_id = self.login_actor()
        self._remove_session(sess_id)
        # session removed from db
        self.assertRaises(SessionNotFound, self.get_session, sess_id)
        # session exists in memcache
        sess_cache = self.mem_cache.get(sess_id.encode('utf8'))
        self.assertNotEqual(None, sess_cache)
        # dumping removed session
        dump_into_db(transaction)
        # session expiration pause
        sleep(settings.session_valid_minutes * 60)

        # checking results
        # session removed from db
        self.assertRaises(SessionNotFound, self.get_session, sess_id)
        # session not exists in memcache
        sess_cache = self.mem_cache.get(sess_id.encode('utf8'))
        print "###", sess_cache
        self.assertEqual(None, sess_cache)


if __name__ == '__main__':
    unittest.main()
