from datetime import datetime
import pytz
import cjson
from uuid import uuid4

from helixcore import mapping
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.server.errors import RequestProcessingError
from helixcore.server.response import response_ok

from helixauth import security
from helixauth.conf.db import transaction
from helixauth.error import (EnvironmentNotFound,
    HelixauthObjectAlreadyExists, UserAuthError, SessionAuthError,
    SessionNotFound, UserNotFound)
from helixauth.db.filters import EnvironmentFilter, SessionFilter, UserFilter
from helixauth.db.dataobject import Environment, User, Session
from helixauth.logic.auth import Authentifier
from helixauth.wsgi.protocol import protocol


#from helixauth.conf.db import transaction
#from helixauth.dataobject import Environment
#from helixauth.error import HelixauthError

#from helixcore.utils import filter_dict

def authentificate(method):
    @detalize_error(UserAuthError, RequestProcessingError.Category.auth, 'login')
    @detalize_error(SessionNotFound, RequestProcessingError.Category.auth, 'session_id')
    def decroated(self, data, curs):
        auth = Authentifier()
        (session, environment, user) = auth.get_credentials(data)
        auth.check_access(session, user)
#        data['user_id'] = user.id
        data.pop('login', None)
        data.pop('password', None)
        data.pop('session_id', None)
        data.pop('custom_user_info', None)
        result = method(self, data, environment, user, curs)
        result['session_id'] = session.session_id
        return result
    return decroated


class Handler(AbstractHandler):
    '''
    Handles all API actions. Method names are called like actions.
    '''

    def ping(self, data): #IGNORE:W0613
        return response_ok()

    def get_api_actions(self, data):
        marker = '_request'
        actions = [c.name for c in protocol if c.name.endswith(marker)]
        actions = map(lambda x: x.replace(marker, ''), actions)
        return response_ok(actions=actions)

    def get_authorized_api_actions(self, data):
        actions = self.get_api_actions(data)
        unauthorized_api_actions = ('ping', 'get_api_actions', 'get_authorized_api_actions')
        actions = filter(lambda x: x not in unauthorized_api_actions, actions)
        return response_ok(actions=actions)

    @transaction()
    @detalize_error(HelixauthObjectAlreadyExists,
        RequestProcessingError.Category.data_integrity, 'name')
    def add_environment(self, data, curs=None):
        # creating environment
        try:
            f = EnvironmentFilter(data, {}, {})
            env = f.filter_one_obj(curs)
            raise HelixauthObjectAlreadyExists('Environment "%s" already exists' % env.name)
        except EnvironmentNotFound, _:
            pass

        env_data = {'name': data.get('name')}
        env = Environment(**env_data)
        mapping.save(curs, env)

        # creating user
        u_data = {'environment_id': env.id, 'login': data.get('su_login'),
            'password': security.encrypt_password(data.get('su_password')),
            'role': User.ROLE_SUPER}
        user = User(**u_data)
        mapping.save(curs, user)

        # creating session
#        session = self._create_session(curs, env, user, {})
        return response_ok(session_id='aaa')

    @transaction()
    @detalize_error(EnvironmentNotFound,
        RequestProcessingError.Category.auth, 'login')
    @detalize_error(UserNotFound,
        RequestProcessingError.Category.auth, 'login')
    def login(self, data, curs=None):
        enc_data = security.encrypt_passwords(data)
        f = EnvironmentFilter(enc_data, {}, {})
        env = f.filter_one_obj(curs)

        f = UserFilter(env, enc_data, {}, {})
        user = f.filter_one_obj(curs)

        # creating session
        auth = Authentifier()
        rights = auth.get_acess_rights(env, user)
        sz_data = cjson.encode({'rights': rights})
        session = auth.create_session(curs, env, user, sz_data)
        return response_ok(session_id=session.session_id)

#    def _get_environment_from_sesion(self, curs, session):
#        f = EnvironmentFilter({'environment_id': session.environment_id}, {}, {})
#        return f.filter_one_obj(curs)
#
#    def _get_user_from_sesion(self, curs, env, session):
#        f = UserFilter(env, {'id': session.user_id}, {}, {})
#        return f.filter_one_obj(curs)

    @transaction()
    @authentificate
#    @detalize_error(HelixauthObjectAlreadyExists,
#        RequestProcessingError.Category.data_integrity, 'name')
    def modify_environment(self, data, env, user, curs=None):
        return response_ok()

