# coding=utf-8
import json
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.conf.db import transaction
from helixauth.logic.auth import Authenticator
from helixcore.server.wsgi_application import RequestInfo
from helixauth.db.dataobject import Service


class AuthTestCase(ActorLogicTestCase):
    def test_salt(self):
        a = Authenticator()
        for _ in xrange(1000):
            s = a.salt()
            self.assertNotEquals(None, s)
            self.assertNotEquals('', s)

    def test_encrypt_password(self):
        a = Authenticator()
        p = a.encrypt_password('pass', 'salt')
        self.assertNotEquals(None, p)
        self.assertNotEquals('', p)

        enc_p1 = a.encrypt_password('1', '2')
        enc_p2 = a.encrypt_password('1', '2')
        self.assertEquals(enc_p1, enc_p2)

        enc_p2 = a.encrypt_password(u'чук', '2')

    @transaction()
    def test_create_restore_password_session(self, curs=None):
        a = Authenticator()
        self.create_actor_env()
        env = self.get_environment_by_name(self.actor_env_name)
        user = self.get_subj_user(env.id, self.actor_login)
        req_info = RequestInfo()
        sess = a.create_restore_password_session(curs, env, user,
            req_info, bind_to_ip=False, lifetime_minutes=None)
        sess_data = json.loads(sess.serialized_data)
        rights = sess_data['rights']
        self.assertEquals({Service.TYPE_AUTH: ['set_password_self']},
            rights)


if __name__ == '__main__':
    unittest.main()