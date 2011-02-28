# coding=utf-8
import unittest

from helixcore.server.api import Api
from helixcore.error import ValidationError

from helixauth.test.root_test import RootTestCase
from helixauth.wsgi.protocol import protocol
import datetime
import pytz


class ProtocolTestCase(RootTestCase):
    api = Api(protocol)

    def validate_error_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'code': 'c', 'message': 'h', 'details': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'code': 'c', 'message': 'h', 'details': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c', 'category': 'test'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'code': 'c', 'category': 'test', 'message': 'm'})

    def validate_authorized_error_response(self, action_name):
        self.api.validate_response(action_name, {'session_id': 'i',
            'status': 'error', 'category': 't', 'code': 'c',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'session_id': 'i',
            'status': 'error', 'category': 't', 'code': 'c',
            'message': 'h', 'details': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 't', 'code': 'c',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test', 'code': 'c'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test', 'code': 'c', 'message': 'm'})

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.validate_error_response(action_name)

    def validate_authorized_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok', 'session_id': 'i'})
        self.validate_authorized_error_response(action_name)

    def test_ping(self):
        a_name = 'ping'
        self.api.validate_request(a_name, {})
        self.validate_status_response(a_name)

    def test_get_api_actions(self):
        a_name = 'get_api_actions'
        self.api.validate_request(a_name, {})
        self.api.validate_response(a_name, {'status': 'ok',
            'actions': ['a', 'b', 'c']})
        self.api.validate_response(a_name, {'status': 'ok',
            'actions': []})
        self.validate_error_response(a_name)

    test_get_auuthorized_api_actions = test_get_api_actions

    def test_login(self):
        a_name = 'login'
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'e', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'login': 'l', 'password': 'p',
            'environment_name': 'n'})
        self.validate_authorized_status_response(a_name)

    def test_logout(self):
        a_name = 'logout'
#        self.api.validate_request(a_name, {'session_id': 'i'})
        self.validate_status_response(a_name)

    def test_add_environment(self):
        a_name = 'add_environment'
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p'})
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p', 'custom_actor_info': None})

        self.api.validate_response(a_name,
            {'status': 'ok', 'session_id': 'i', 'environment_id': 1})
        self.validate_authorized_error_response(a_name)

    def test_get_environment(self):
        a_name = 'get_environment'
        self.api.validate_request(a_name, {'session_id': 'i'})

        self.api.validate_response(a_name, {'status': 'ok', 'environment': {
            'id': 4,'name': 'n'}})
        self.validate_error_response(a_name)

    def test_modify_environment(self):
        a_name = 'modify_environment'
        self.api.validate_request(a_name, {'session_id': 'i',
            'custom_actor_info': 'i', 'new_name': 'n'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'new_name': 'n'})
        self.validate_status_response(a_name)

    def test_add_user(self):
        a_name = 'add_user'
        self.api.validate_request(a_name, {'session_id': 'i',
            'login': 'l', 'password': 'p', 'role': 'user'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'login': 'l', 'password': 'p', 'role': 'user', 'is_active': False})
        self.api.validate_request(a_name, {'session_id': 'i',
            'login': 'l', 'password': 'p', 'is_active': False,
            'groups_ids': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'login': 'l', 'password': 'p', 'is_active': False,
            'groups_ids': [1, 2, 3]})

        self.api.validate_response(a_name,
            {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_modify_password(self):
        a_name = 'modify_password'
        self.api.validate_request(a_name, {'session_id': 'i',
            'old_password': 'p', 'new_password': 'pp'})

        self.validate_status_response(a_name)

    def test_get_users(self):
        a_name = 'get_users'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': []},
            'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': [1, 2, 3]},
            'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': [1, 2, 3]},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['-id']})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'groups_ids': [3, 4], 'login': 'jack'},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['-id']})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'roles': ['super'], 'id': 4},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['-id']})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'roles': [], 'id': 4},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['-id']})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2, 'users': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'users': [
                {'id': 42, 'login': 'l', 'is_active': True, 'role': 'user', 'groups_ids': [],},
            ]
        })
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'users': [
                {'id': 42, 'login': 'l', 'is_active': True, 'role': 'user', 'groups_ids': [],},
                {'id': 24, 'login': 'l', 'is_active': True, 'role': 'user', 'groups_ids': [1, 2],},
            ]
        })
        self.validate_error_response(a_name)

    def test_add_service(self):
        a_name = 'add_service'
        self.api.validate_request(a_name, {'session_id': 'i',
            'name': 'n', 'type': 't', 'properties': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'name': 'n', 'type': 't', 'properties': ['a', 'b', 'c']})
        self.api.validate_request(a_name, {'session_id': 'i',
            'name': 'n', 'type': 't', 'properties': ['a', 'b', 'c'],
            'is_active': False})

        self.api.validate_response(a_name,
            {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

    def test_get_services(self):
        a_name = 'get_services'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': []},
            'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': [1, 2, 3]},
            'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': [1, 2, 3]},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['name', '-id']})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'type': 't'},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['name', '-id']})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'services': [
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'services': [
            {
                'id': 42, 'is_active': True, 'is_possible_deactiate': True,
                'properties': [], 'name': u'сервис0', 'type': 't',
            },
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'services': [
            {
                'id': 42, 'is_active': True, 'is_possible_deactiate': True,
                'properties': [], 'name': u'сервис0', 'type': 't',
            },
            {
                'id': 43, 'is_active': True, 'is_possible_deactiate': True,
                'properties': ['a', 'b', u'омега'], 'name': u'сервис0',
                'type': 't',
            },
        ]})
        self.validate_error_response(a_name)

    def test_modify_service(self):
        a_name = 'modify_service'
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_name': 'n'})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_name': 'n', 'new_properties': ['a', 'b']})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_name': 'n', 'new_properties': ['a', 'b'],
            'new_is_active': False})

        self.validate_status_response(a_name)

    def test_add_group(self):
        a_name = 'add_group'
        self.api.validate_request(a_name, {'session_id': 'i', 'name': 'n',
            'rights': [{'service_id': 1, 'properties': []}]})
        self.api.validate_request(a_name, {'session_id': 'i', 'name': 'n',
            'rights': [{'service_id': 1, 'properties': ['c']}],
            'is_active': True})
        self.api.validate_request(a_name, {'session_id': 'i', 'name': 'n',
            'rights': [{'service_id': 1, 'properties': ['a', 'b']}],
            'is_active': False})

        self.validate_status_response(a_name)

    def test_modify_group(self):
        a_name = 'modify_group'
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_is_active': True})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_is_active': False, 'new_name': 'nn', 'new_rights': []})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_is_active': False, 'new_rights': [{'service_id': 1,
            'properties': []}]})
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1,
            'new_is_active': False, 'new_rights': [{'service_id': 1,
            'properties': ['a', 'b']}]})

        self.validate_status_response(a_name)

    def test_delete_group(self):
        a_name = 'delete_group'
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1})
        self.validate_status_response(a_name)

    def test_get_groups(self):
        a_name = 'get_groups'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': []},
            'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': [1, 2, 3]},
            'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'ids': [1, 2, 3]},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['name', '-id']})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'name': 't', 'is_active': True},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['name', '-id']})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'groups': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'groups': [
            {
                'id': 42, 'is_active': True, 'name': u'группа0',
                'rights': [{'service_id': 1, 'properties': []}],
            },
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'groups': [
            {
                'id': 42, 'is_active': True, 'name': u'группа0',
                'rights': [{'service_id': 1, 'properties': []}],
            },
            {
                'id': 43, 'is_active': False, 'name': u'группа1',
                'rights': [{'service_id': 1, 'properties': ['a', 'b']}],
            },
        ]})
        self.validate_error_response(a_name)

    def test_get_action_logs(self):
        a_name = 'get_action_logs'
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {}, 'paging_params': {'limit': 0, 'offset': 0,},})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'from_request_date': '2011-02-21 00:00:00',
            'to_request_date': '2011-02-21 23:59:59'},
            'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'action': 'a'}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'actor_user_id': 1}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_user_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_user_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
            {
                'id': 43, 'session_id': None, 'custom_actor_user_info': 'some info',
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.2', 'request': 'req',
                'response': 'resp'
            },
            {
                'id': 44, 'session_id': 's_id', 'custom_actor_user_info': 'some info',
                'subject_users_ids': [3], 'actor_user_id': None, 'action': 'login',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.2', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_get_user_rights(self):
        a_name = 'get_user_rights'
        self.api.validate_request(a_name, {'session_id': 's'})

        self.api.validate_response(a_name, {'status': 'ok',
            'rights':[{'service_id': 1, 'service_type': 't',
            'properties': []}]})
        self.api.validate_response(a_name, {'status': 'ok',
            'rights':[{'service_id': 1, 'service_type': 't',
            'properties': ['a']}]})
        self.api.validate_response(a_name, {'status': 'ok',
            'rights':[{'service_id': 1, 'service_type': 't',
            'properties': ['a', u'я']}]})
        self.validate_error_response(a_name)

    def test_check_access(self):
        a_name = 'check_access'
        self.api.validate_request(a_name, {'session_id': 's',
            'service_type': 't', 'property': 'p'})
        self.api.validate_request(a_name, {'session_id': 's', 'service_id': 1,
            'service_type': 't', 'property': 'p'})
        self.validate_status_response(a_name)


if __name__ == '__main__':
    unittest.main()
