import unittest
from time import sleep
import memcache

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixauth.conf import settings
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

    @transaction()
    def test_clean(self, curs=None):
        self.create_actor_env()
        self.login_actor()
        self.login_actor()
        self.login_actor()
        f = SessionFilter({}, {}, None)
        sess_cnt = f.filter_objs_count(curs)
        self.assertTrue(sess_cnt > 0)

        sleep(settings.session_valid_minutes * 60)
        session_utils.clean(transaction)
        sess_cnt = f.filter_objs_count(curs)
        self.assertEquals(0, sess_cnt)

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
        pass


if __name__ == '__main__':
    unittest.main()
