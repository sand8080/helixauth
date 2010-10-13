import cjson
from datetime import timedelta

from helixcore import mapping
from helixcore.server.api import Api

# must be imported first in helixauth set
from helixauth.test.db_based_test import DbBasedTestCase

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.filters import EnvironmentFilter, SessionFilter,\
    SubjectUserFilter
from helixauth.logic import actions, auth
from helixauth.wsgi.protocol import protocol


class LogicTestCase(DbBasedTestCase):
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
    def get_subj_user(self, environment_id, login, password, curs=None):
        a = auth.Authentifier()
        filter_params = {'environment_id': environment_id,
            'login': login, 'password': a.encrypt_password(password)}
        f = SubjectUserFilter(environment_id, filter_params, {}, {})
        return f.filter_one_obj(curs)

    def add_environment(self, **kwargs):
        response = self.handle_action('add_environment', kwargs)
        name = kwargs['name']
        env = self.get_environment_by_name(name)
        self.assertEqual(name, env.name)

        self.assertNotEqual(None, response.get('session_id'))
        login = kwargs['su_login']
        password = kwargs['su_password']
        user = self.get_subj_user(env.id, login, password)

        self.assertEqual(login, user.login)
        self.assertEqual(env.id, user.environment_id)
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
        return self.handle_action('login', kwargs)

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

    def check_response_ok(self, resp):
        self.assertEqual('ok', resp['status'])

    @transaction()
    def inactivate_user(self, user, curs=None):
        user.is_active = False
        mapping.save(curs, user)

    def add_user(self, **kwargs):
        response = self.handle_action('add_user', kwargs)
        return response

    def add_service(self, **kwargs):
        resp = self.handle_action('add_service', kwargs)
        return resp

    def get_services(self, **kwargs):
        resp = self.handle_action('get_services', kwargs)
        return resp

    def modify_users_rights(self, **kwargs):
        resp = self.handle_action('modify_users_rights', kwargs)
        return resp

    def get_authorized_api_actions(self):
        return self.handle_action('get_authorized_api_actions', {})