# coding=utf-8
import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.server.errors import RequestProcessingError
from helixauth.db.filters import ServiceFilter
from helixauth.conf.db import transaction
from helixauth.db.dataobject import Service


class ServiceTestCase(ActorLogicTestCase):
    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.create_actor_env()

    @transaction()
    def test_default_service_created(self, curs=None):
        env = self.get_environment_by_name(self.actor_env_name)
        f = ServiceFilter(env.id, {}, {}, None)
        s = f.filter_one_obj(curs)
        self.assertEqual('Auth', s.name)
        self.assertEqual(env.id, s.environment_id)
        self.assertEqual(True, s.is_active)
        self.assertEqual(False, s.is_possible_deactiate)

        resp = self.get_authorized_api_actions()
        self.check_response_ok(resp)
        auth_a = resp['actions']
        self.assertEqual(auth_a, s.properties)

    def test_add_service(self):
        session_id = self.login_actor()
        req_srv = {'session_id': session_id, 'name': u'сервис0',
            'type': Service.TYPE_BILLING, 'properties': ['alpha', u'бетта']}
        resp = self.add_service(**req_srv)
        self.check_response_ok(resp)

        # same type service in another environment
        req = {'name': 'zero', 'su_login': self.actor_login,
            'su_password': self.actor_password}
        self.add_environment(**req)
        req = {'environment_name': 'zero',
            'login': self.actor_login, 'password': self.actor_password}
        resp = self.login(**req)
        self.check_response_ok(resp)
        req_srv['session_id'] = resp['session_id']
        resp = self.add_service(**req_srv)
        self.check_response_ok(resp)

    def test_add_duplicate_services(self):
        session_id = self.login_actor()
        req = {'session_id': session_id, 'name': u'сервис0',
            'type': Service.TYPE_BILLING, 'properties': ['alpha', u'бетта']}
        resp = self.add_service(**req)
        self.check_response_ok(resp)
        self.assertRaises(RequestProcessingError, self.add_service, **req)

    def test_get_services(self):
        session_id = self.login_actor()
        req = {'session_id': session_id, 'properties': ['alpha', u'бетта']}
        s_num = 10
        for i in xrange(s_num - 1): # one service already exists
            req['name'] = u'сервис_%d' % i
            req['type'] = u'тип_%d' % i
            self.add_service(**req)

        req = {'session_id': session_id, 'filter_params': {},
            'paging_params': {}, 'ordering_params': ['name']}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertEqual(s_num, resp['total'])
        self.assertEqual(s_num, len(resp['services']))

        l_num = 3
        req = {'session_id': session_id, 'filter_params': {},
            'paging_params': {'limit': l_num}, 'ordering_params': ['name']}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertEqual(s_num, resp['total'])
        self.assertEqual(min(l_num, s_num), len(resp['services']))

        l_num = 2
        s_ids = [1, 2, 3, 4]
        req = {'session_id': session_id, 'paging_params': {'limit': l_num},
            'filter_params': {'services_ids': s_ids},
            'ordering_params': ['name']}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertEqual(len(s_ids), resp['total'])
        self.assertEqual(min(len(s_ids), l_num), len(resp['services']))

        l_num = 3
        s_types = [u'тип_0', u'тип_3', u'тип_1000']
        req = {'session_id': session_id, 'paging_params': {'limit': l_num},
            'filter_params': {'services_types': s_types},
            'ordering_params': ['name']}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertEqual(len(s_types) - 1, resp['total'])
        self.assertEqual(min(len(s_types) - 1, l_num), len(resp['services']))

    def test_modify_service(self, curs=None):
        session_id = self.login_actor()
        env = self.get_environment_by_name(self.actor_env_name)
        srv = self.load_auth_service(env.id)

        # changing service name
        n_name = 'NEW Auth'
        req = {'session_id': session_id, 'service_id': srv.id,
            'new_name': n_name}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)
        n_srv = self.load_auth_service(env.id)
        self.assertEqual(n_name, n_srv.name)

        # changing service properties
        n_properties = ['a', 'b', 'c']
        req = {'session_id': session_id, 'service_id': srv.id,
            'new_properties': n_properties}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)
        n_srv = self.load_auth_service(env.id)
        self.assertEqual(n_properties, n_srv.properties)

        req = {'session_id': session_id, 'service_id': srv.id,
            'new_is_active': False}
        self.assertRaises(RequestProcessingError, self.modify_service, **req)

    def test_modify_service_name_to_existed(self):
        session_id = self.login_actor()
        env = self.get_environment_by_name(self.actor_env_name)
        srv = self.load_auth_service(env.id)

        name_another = 'another %s' % srv.name
        req = {'session_id': session_id, 'name': name_another,
            'properties': [], 'type': Service.TYPE_BILLING}
        resp = self.add_service(**req)
        self.check_response_ok(resp)
        srv_another = self.load_service(env.id, name_another)

        req = {'session_id': session_id, 'service_id': srv_another.id,
            'new_name': srv.name}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)


if __name__ == '__main__':
    unittest.main()