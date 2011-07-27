import unittest
from time import sleep

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase

from helixauth.conf import settings
settings.session_valid_minutes = 0.01

from helixauth.conf.db import transaction
from helixauth.db.filters import SessionFilter
from helixauth.logic import session_cleaner

class ServiceTestCase(ActorLogicTestCase):
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
        session_cleaner.clean()
        sess_cnt = f.filter_objs_count(curs)
        self.assertEquals(0, sess_cnt)


if __name__ == '__main__':
    unittest.main()