# coding=utf-8
import datetime
import pytz
import unittest

from helixcore.server.api import Api
from helixcore.test.utils_for_testing import ProtocolTester

from helixauth.test.root_test import RootTestCase
from helixauth.wsgi.protocol import protocol


class ProtocolTestCase(RootTestCase, ProtocolTester):
    api = Api(protocol)

    def test_login(self):
        a_name = 'login'
        self.api.validate_request(a_name, {'email': 'l@h.com', 'password': 'p',
            'environment_name': 'e', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'email': 'l@h.com', 'password': 'p',
            'environment_name': 'n'})
        self.api.validate_request(a_name, {'email': 'l@h.com', 'password': 'p',
            'environment_name': 'n', 'bind_to_ip': False})
        self.api.validate_request(a_name, {'email': 'l@h.com', 'password': 'p',
            'environment_name': 'n', 'bind_to_ip': True})
        self.api.validate_request(a_name, {'email': 'l@h.com', 'password': 'p',
            'environment_name': 'n', 'bind_to_ip': True,
            'fixed_lifetime_minutes': 21})

        self.api.validate_response(a_name, {'status': 'ok', 'session_id': 'i',
            'user_id': 5, 'environment_id': 7})
        self.validate_error_response(a_name)

    def test_logout(self):
        a_name = 'logout'
        self.api.validate_request(a_name, {'session_id': 'i'})
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

    def test_get_api_scheme(self):
        a_name = 'get_api_scheme'
        self.api.validate_request(a_name, {'session_id': 'i'})

        self.api.validate_response(a_name, {'status': 'ok',
            'scheme': 'html table content'})
        self.validate_error_response(a_name)

    def test_add_environment(self):
        a_name = 'add_environment'
        self.api.validate_request(a_name, {'name': 'n', 'su_email': 'l@h.com',
            'su_password': 'p'})
        self.api.validate_request(a_name, {'name': 'n', 'su_email': 'l@h.com',
            'su_password': 'p', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'name': 'n', 'su_email': 'l@h.com',
            'su_password': 'p', 'custom_actor_info': None})

        self.api.validate_response(a_name,
            {'status': 'ok', 'session_id': 'i', 'environment_id': 1,
                'user_id': 3})
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
            'email': 'l@h.com', 'password': 'p', 'role': 'user'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'email': 'l@h.com', 'password': 'p', 'role': 'user', 'is_active': False})
        self.api.validate_request(a_name, {'session_id': 'i',
            'email': 'l@h.com', 'password': 'p', 'is_active': False,
            'groups_ids': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'email': 'l@h.com', 'password': 'p', 'is_active': False,
            'groups_ids': [1, 2, 3]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'email': 'l@h.com', 'password': 'p', 'is_active': False,
            'groups_ids': [1, 2, 3], 'lang': 'en'})

        self.api.validate_response(a_name,
            {'status': 'ok', 'id': 1, 'notification': {'is_sent': False,
                'is_processable': True, 'message_data': {},
                'checking_steps': []}})
        self.api.validate_response(a_name,
            {'status': 'ok', 'id': 1, 'notification': {'is_sent': True,
                'is_processable': False, 'message_data': {},
                'checking_steps': ['a', 'b']}})
        self.validate_error_response(a_name)

    def test_modify_user_self(self):
        a_name = 'modify_user_self'
        self.api.validate_request(a_name, {'session_id': 'i',
            'old_password': 'p', 'new_password': 'pp',
            'new_lang': 'en'})

        self.validate_status_response(a_name)

    def test_set_password_self(self):
        a_name = 'set_password_self'
        self.api.validate_request(a_name, {'session_id': 'i',
            'new_password': 'pp'})

        self.validate_status_response(a_name)

    def test_modify_users(self):
        a_name = 'modify_users'
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_email': 'l@h.com'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_password': 'p'})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_is_active': False})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_groups_ids': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_groups_ids': [1]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_groups_ids': [1, 2]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_groups_ids': [1, 2],
            'new_lang': 'ru'})

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
            'filter_params': {'groups_ids': [3, 4], 'email': 'ja*@h.com'},
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
                {'id': 42, 'email': 'l@h.com', 'is_active': True,
                    'role': 'user', 'groups_ids': [], 'lang': 'ru'},
            ]
        })
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'users': [
                {'id': 42, 'email': 'l@h.com', 'is_active': True,
                    'role': 'user', 'groups_ids': [], 'lang': 'en'},
                {'id': 24, 'email': 'l@h.com', 'is_active': True,
                    'role': 'user', 'groups_ids': [1, 2], 'lang': 'ru'},
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
            'filter_params': {'id': 4, 'type': 't'},
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

    def test_delete_service(self):
        a_name = 'delete_service'
        self.api.validate_request(a_name, {'session_id': 'i', 'id': 1})
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

        self.api.validate_response(a_name, {'status': 'ok', 'id': 1})
        self.validate_error_response(a_name)

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
            'filter_params': {'user_id': 1}, 'paging_params': {}})
        self.api.validate_request(a_name, {'session_id': 's',
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
            {
                'id': 43, 'session_id': None, 'custom_actor_info': 'some info',
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.2', 'request': 'req',
                'response': 'resp'
            },
            {
                'id': 44, 'session_id': 's_id', 'custom_actor_info': 'some info',
                'subject_users_ids': [3], 'actor_user_id': None, 'action': 'login',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.2', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.validate_error_response(a_name)

    def test_get_action_logs_self(self):
        a_name = 'get_action_logs_self'
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
            'filter_params': {'session_id': ''}, 'paging_params': {}})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'action_logs': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
        ]})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'action_logs': [
            {
                'id': 42, 'session_id': 's_id', 'custom_actor_info': None,
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.1', 'request': 'req',
                'response': 'resp'
            },
            {
                'id': 43, 'session_id': None, 'custom_actor_info': 'some info',
                'subject_users_ids': [3], 'actor_user_id': 1, 'action': 'a',
                'request_date': '%s' % datetime.datetime.now(pytz.utc),
                'remote_addr': '127.0.0.2', 'request': 'req',
                'response': 'resp'
            },
            {
                'id': 44, 'session_id': 's_id', 'custom_actor_info': 'some info',
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

        self.api.validate_response(a_name, {'status': 'ok',
            'user_id': 1, 'environment_id': 1, 'access': 'granted'})
        self.api.validate_response(a_name, {'status': 'ok',
            'user_id': 1, 'environment_id': 1, 'access': 'denied'})
        self.validate_error_response(a_name)

    def test_check_user_exist_access(self):
        a_name = 'check_user_exist'
        self.api.validate_request(a_name, {'session_id': 's',
            'id': 1})

        self.api.validate_response(a_name, {'status': 'ok',
            'exist': True})
        self.api.validate_response(a_name, {'status': 'ok',
            'exist': False})
        self.validate_error_response(a_name)

    def test_get_notifications(self):
        a_name = 'get_notifications'
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
            'filter_params': {'id': 3, 'is_active': True, 'type': 'email'},
            'paging_params': {'limit': 0, 'offset': 0,},
            'ordering_params': ['-id']})

        self.api.validate_response(a_name, {'status': 'ok', 'total': 2,
            'notifications': []})
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'notifications': [
                {'id': 42, 'event': 'e', 'is_active': True,
                    'type': 'email', 'messages': [{'lang': 'ru',
                    'email_subj': 's', 'email_msg': 'm'},
                    {'lang': 'en', 'email_subj': 's', 'email_msg': 'm'}]
                },
            ]
        })
        self.api.validate_response(a_name, {'status': 'ok', 'total': 4,
            'notifications': [
                {'id': 42, 'event': 'e', 'is_active': True,
                    'type': 'email', 'messages': [{'lang': 'en',
                    'email_subj': 'ss', 'email_msg': 'mm'},
                    {'lang': 'ru', 'email_subj': 'sss',
                    'email_msg': 'mmm'}]},
                {'id': 42, 'event': 'e', 'is_active': True,
                    'type': 'email', 'messages': [{'lang': 'ru',
                    'email_subj': 's', 'email_msg': 'm'}]},
            ]
        })
        self.validate_error_response(a_name)

    def test_modify_notifications(self):
        a_name = 'modify_notifications'
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_is_active': True})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_is_active': False})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_messages': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2], 'new_messages': [
                {'lang': 'en', 'email_subj': 's', 'email_msg': 'm'},
                {'lang': 'ru', 'email_subj': 'ss', 'email_msg': 'mm'},
            ]})

        self.validate_status_response(a_name)

    def test_reset_notifications(self):
        a_name = 'reset_notifications'
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': []})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1]})
        self.api.validate_request(a_name, {'session_id': 'i',
            'ids': [1, 2]})
        self.validate_status_response(a_name)


if __name__ == '__main__':
    unittest.main()
