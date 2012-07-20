# coding=utf-8
import unittest
import json

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError
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
        srvs = f.filter_objs(curs)
        s_auth = srvs[0]
        s_billing = srvs[1]

        self.assertEqual('Auth', s_auth.name)
        self.assertEqual(env.id, s_auth.environment_id)
        self.assertEqual(True, s_auth.is_active)
        self.assertEqual(False, s_auth.is_possible_deactiate)

        resp = self.get_authorized_api_actions()
        self.check_response_ok(resp)
        auth_a = resp['actions']

        srv_props = json.loads(s_auth.serialized_properties)
        self.assertEqual(auth_a, srv_props)

        self.assertEqual('Billing', s_billing.name)
        self.assertEqual(env.id, s_billing.environment_id)
        self.assertEqual(True, s_billing.is_active)
        self.assertEqual(True, s_billing.is_possible_deactiate)

    def test_add_service(self):
        session_id = self.login_actor()
        req_srv = {'session_id': session_id, 'name': u'сервис0',
            'type': 'new_service', 'properties': ['alpha', u'бетта']}
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
        self.assertRaises(RequestProcessingError, self.add_service, **req)

    def test_get_services(self):
        session_id = self.login_actor()

        req = {'session_id': session_id, 'filter_params': {},
            'paging_params': {}, 'ordering_params': ['name']}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        existed_num = resp['total']

        req = {'session_id': session_id, 'properties': ['alpha', u'бетта']}
        s_num = 10
        for i in xrange(s_num - existed_num): #  service already exists
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
            'filter_params': {'ids': s_ids},
            'ordering_params': ['name']}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertEqual(len(s_ids), resp['total'])
        self.assertEqual(min(len(s_ids), l_num), len(resp['services']))

        l_num = 3
        s_types = [u'тип_0', u'тип_3', u'тип_1000']
        req = {'session_id': session_id, 'paging_params': {'limit': l_num},
            'filter_params': {'types': s_types},
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
        req = {'session_id': session_id, 'id': srv.id,
            'new_name': n_name}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)
        n_srv = self.load_auth_service(env.id)
        self.assertEqual(n_name, n_srv.name)

        # changing service properties
        n_properties = ['a', 'b', 'c']
        req = {'session_id': session_id, 'id': srv.id,
            'new_properties': n_properties}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)
        n_srv = self.load_auth_service(env.id)
        self.assertEqual(n_properties, json.loads(n_srv.serialized_properties))

        req = {'session_id': session_id, 'id': srv.id,
            'new_is_active': False}
        self.assertRaises(RequestProcessingError, self.modify_service, **req)

    def test_modify_service_name_to_existed(self):
        session_id = self.login_actor()
        env = self.get_environment_by_name(self.actor_env_name)
        srv = self.load_auth_service(env.id)

        name_another = 'another %s' % srv.name
        req = {'session_id': session_id, 'name': name_another,
            'properties': [], 'type': 'new_type'}
        resp = self.add_service(**req)
        self.check_response_ok(resp)
        srv_another = self.load_service(env.id, name_another)

        req = {'session_id': session_id, 'id': srv_another.id,
            'new_name': srv.name}
        resp = self.modify_service(**req)
        self.check_response_ok(resp)

    def test_deleting_unknown_service_failed(self, curs=None):
        session_id = self.login_actor()
        req = {'session_id': session_id, 'id': 99999}
        self.assertRaises(RequestProcessingError, self.delete_service, **req)

    def test_deleting_auth_service_failed(self, curs=None):
        session_id = self.login_actor()
        env = self.get_environment_by_name(self.actor_env_name)
        srv = self.load_auth_service(env.id)
        req = {'session_id': session_id, 'id': srv.id}
        self.assertRaises(RequestProcessingError, self.delete_service, **req)

    def test_delete_service(self, curs=None):
        session_id = self.login_actor()

        req = {'session_id': session_id, 'filter_params': {'type': Service.TYPE_BILLING},
            'paging_params': {}}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertTrue(resp['total'] > 0)

        srv_id = resp['services'][0]['id']
        req = {'session_id': session_id, 'id': srv_id}
        resp = self.delete_service(**req)
        self.check_response_ok(resp)

        req = {'session_id': session_id, 'filter_params': {'id': srv_id},
            'paging_params': {}}
        resp = self.get_services(**req)
        self.check_response_ok(resp)
        self.assertEquals(0, resp['total'])


if __name__ == '__main__':
    unittest.main()