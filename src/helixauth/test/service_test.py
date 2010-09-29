import cjson
from datetime import timedelta

from helixcore import mapping
from helixcore.server.api import Api

# must be imported first in helixauth set
from helixauth.test.db_based_test import DbBasedTestCase
from helixauth import security
from helixauth.db.filters import EnvironmentFilter, UserFilter, SessionFilter
from helixauth.conf.db import transaction
from helixauth.logic import actions
from helixauth.wsgi.protocol import protocol
from helixauth.conf import settings


class ServiceTestCase(DbBasedTestCase):
    def handle_action(self, action, data):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(cjson.encode(request))
        response = actions.handle_action(action_name, dict(data))
        api.handle_response(action_name, dict(response))
        return response

    @transaction()
    def get_environment_by_name(self, name, curs=None):
        f = EnvironmentFilter({'name': name}, {}, {})
        return f.filter_one_obj(curs)

    @transaction()
    def get_auth_user(self, environment, login, password, curs=None):
        filter_params = {'environment_id': environment.id,
            'login': login, 'password': security.encrypt_password(password)}
        f = UserFilter(environment, filter_params, {}, {})
        return f.filter_one_obj(curs)

    def add_environment(self, name, su_login, su_password, custom_user_info=None):
        response = self.handle_action('add_environment', {'name': name, 'su_login': su_login,
            'su_password': su_password, 'custom_user_info': custom_user_info})
        environment = self.get_environment_by_name(name)
        self.assertEqual(name, environment.name)

        user = self.get_auth_user(environment, su_login, su_password)
        self.assertEqual(su_login, user.login)
        self.assertEqual(environment.id, user.environment_id)
        self.check_response_ok(response)
        session_id = response.get('session_id')
        self.assertNotEqual(None, session_id)
        return response

    def modify_environment(self, **kwargs):
        response = self.handle_action('modify_environment', kwargs)
        self.check_response_ok(response)
        env_new = self.get_environment_by_name(kwargs['new_name'])
        self.assertEqual(kwargs['new_name'], env_new.name)
        return response

    def login(self, **kwargs):
        response = self.handle_action('login', kwargs)
        return response

    @transaction()
    def get_session(self, session_id, for_update=False, curs=None):
        f = SessionFilter({'session_id': session_id}, {}, {})
        return f.filter_one_obj(curs, for_update=for_update)

    @transaction()
    def make_session_expired(self, session_id, curs=None):
        td = timedelta(minutes=settings.session_valid_minutes)
        session = self.get_session(session_id, for_update=True)
        session.start_date = session.start_date - td
        session.update_date = session.update_date - td
        mapping.save(curs, session)

    def check_response_ok(self, response):
        self.assertEqual('ok', response['status'])

