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

    def validate_status_response(self, action_name):
        self.api.validate_response(action_name, {'status': 'ok'})
        self.validate_error_response(action_name)

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

    def test_add_environment(self):
        a_name = 'add_environment'
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p'})
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p', 'custom_user_info': 'i'})
        self.api.validate_request(a_name, {'name': 'n', 'su_login': 'l',
            'su_password': 'p', 'custom_user_info': None})
        self.validate_status_response(a_name)


if __name__ == '__main__':
    unittest.main()
