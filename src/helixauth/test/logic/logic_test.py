import json
from datetime import timedelta

from helixcore import mapping
from helixcore.server.api import Api
from helixcore.server.wsgi_application import RequestInfo
from helixcore.test.utils_for_testing import get_api_calls

# must be imported first in helixauth set
from helixauth.test.db_based_test import DbBasedTestCase

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.filters import (EnvironmentFilter, SessionFilter,
    SubjectUserFilter, ServiceFilter)
from helixauth.logic import actions
from helixauth.wsgi.protocol import protocol


class LogicTestCase(DbBasedTestCase):
    def handle_action(self, action, data, req_info):
        api = Api(protocol)
        request = dict(data, action=action)
        action_name, data = api.handle_request(json.dumps(request))
        response = actions.handle_action(action_name, dict(data), req_info)
        api.handle_response(action_name, dict(response))
        return response

    @transaction()
    def get_environment_by_name(self, name, curs=None):
        f = EnvironmentFilter({'name': name}, {}, {})
        return f.filter_one_obj(curs)

    @transaction()
    def get_subj_user(self, environment_id, login, password, curs=None):
        filter_params = {'environment_id': environment_id, 'login': login}
        f = SubjectUserFilter(environment_id, filter_params, {}, {})
        return f.filter_one_obj(curs)

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

    @transaction()
    def inactivate_user(self, user, curs=None):
        user.is_active = False
        mapping.save(curs, user)

    def check_response_ok(self, resp):
        self.assertEqual('ok', resp['status'])

    @transaction()
    def load_auth_service(self, env_id, curs=None):
        f = ServiceFilter(env_id, {}, {'limit': 1}, ['id'])
        return f.filter_one_obj(curs)

    @transaction()
    def load_service(self, env_id, name, curs=None):
        f = ServiceFilter(env_id, {'name': name}, {}, None)
        return f.filter_one_obj(curs)


def make_api_call(f_name):
    def m(self, **kwargs):
        req_info = RequestInfo(remote_addr='helixauth.test.ip')
        return self.handle_action(f_name, kwargs, req_info)
    m.__name__ = f_name
    return m


methods = get_api_calls(protocol)
for method_name in methods:
    setattr(LogicTestCase, method_name, make_api_call(method_name))
