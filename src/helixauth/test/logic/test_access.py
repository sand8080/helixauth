import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixauth.db.dataobject import Service
from helixcore.error import RequestProcessingError


class AccessTestCase(ActorLogicTestCase):
    def test_check_access_super_user(self):
        self.create_actor_env()
        sess_id = self.login_actor()
        resp = self.check_access(**{
            'session_id': sess_id, 'property': 'check_access',
            'service_type': Service.TYPE_AUTH})
        self.check_response_ok(resp)

    def test_access_limited_user(self):
        self.create_actor_env()
        session_id = self.login_actor()

        # creating another service
        req = {'session_id': session_id, 'name': 's1', 'type': 'ts1',
            'properties': ['a', 'b']}
        resp = self.add_service(**req)
        self.check_response_ok(resp)

        # adding limited user
        req = {'session_id': session_id, 'login': 'u0', 'password': 'p0'}
        resp = self.add_user(**req)
        self.check_response_ok(resp)
        u_id = resp['user_id']
        granted = {'check_access': True}
        env = self.get_environment_by_name(self.actor_env_name)
        srv = self.load_auth_service(env.id)
        req = {'session_id': session_id, 'subject_users_ids': [u_id],
            'rights': [{'service_id': srv.id, 'properties': granted}]}
        self.modify_users_rights(**req)

        # login limited user
        req = {'environment_name': env.name, 'login': 'u0', 'password': 'p0'}
        resp = self.login(**req)
        self.check_response_ok(resp)
        u_sess_id = resp['session_id']

        # checking access granted to service properties
        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'check_access'}
        resp = self.check_access(**req)
        self.check_response_ok(resp)

        req = {'session_id': u_sess_id, 'service_type': Service.TYPE_AUTH,
            'property': 'add_user'}
        self.assertRaises(RequestProcessingError, self.check_access, **req)


if __name__ == '__main__':
    unittest.main()