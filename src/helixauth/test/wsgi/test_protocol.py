import unittest

from helixcore.server.api import Api
from helixcore.server.errors import ValidationError

from helixauth.test.root_test import RootTestCase
from helixauth.wsgi.protocol import protocol


class ProtocolTestCase(RootTestCase):
    api = Api(protocol)

    def validate_error_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test', 'message': 'm'})

    def validate_authorized_error_response(self, action_name):
        self.api.validate_response(action_name, {'session_id': 'i',
            'status': 'error', 'category': 't',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.api.validate_response(action_name, {'session_id': 'i',
            'status': 'error', 'category': 't',
            'message': 'h', 'details': [{}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 't',
            'message': 'h', 'details': [{'f': 'v'}]})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test'})
        self.assertRaises(ValidationError, self.api.validate_response, action_name,
            {'status': 'error', 'category': 'test', 'message': 'm'})

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.validate_error_response(action_name)

    def validate_authorized_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok', 'session_id': 'i'})
        self.validate_authorized_error_response(action_name)

    def test_ping(self):
        self.api.validate_request('ping', {})
        self.validate_status_response('ping')

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

    def test_add_environment(self):
        a_name = 'add_environment'
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p'})
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p', 'custom_actor_info': 'i'})
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p', 'custom_actor_info': None})
        self.validate_authorized_status_response(a_name)

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
            'login': 'l', 'password': 'p', 'role': 'super', 'is_active': False})
        self.validate_status_response(a_name)


if __name__ == '__main__':
    unittest.main()
