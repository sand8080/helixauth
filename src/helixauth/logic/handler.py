import datetime
import pytz
from uuid import uuid4

from helixcore import mapping
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.misc import security
from helixcore.server.errors import RequestProcessingError
from helixcore.server.response import response_ok

from helixauth.conf.db import transaction
from helixauth.error import (EnvironmentNotFound,
    HelixauthObjectAlreadyExists, UserAuthError, SessionAuthError)
from helixauth.db.filters import EnvironmentFilter
from helixauth.db.dataobject import Environment, User, Session
from helixauth.wsgi.protocol import protocol
import cjson


#from helixauth.conf.db import transaction
#from helixauth.dataobject import Environment
#from helixauth.error import HelixauthError

#from helixcore.utils import filter_dict


def authentificate(method):
    @detalize_error(UserAuthError, RequestProcessingError.Category.auth, 'login')
    @detalize_error(SessionAuthError, RequestProcessingError.Category.auth, 'session_id')
    def decroated(self, data, curs):
        user = self.get_user(curs, data)
        data['user_id'] = user.id
        data.pop('login', None)
        data.pop('password', None)
        data.pop('session_id', None)
        data.pop('custom_user_info', None)
        return method(self, data, user, curs)
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

    def get_user(self, curs, data):
        if 'session_id' in data:
            session_id = data['session_id']
        else:
            login = data['login']
            password = data['password']
#            UserFilter
#        return selector.get_auth_opertator(curs, data['login'], data['password'])

    @transaction()
    @detalize_error(HelixauthObjectAlreadyExists,
        RequestProcessingError.Category.data_integrity, 'name')
    def add_environment(self, data, curs=None):
        # creating environment
        try:
            f = EnvironmentFilter(data, {}, {})
            env = f.filter_one_obj(curs)
            raise HelixauthObjectAlreadyExists('Environment "%s" already exist' % env.name)
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
        session = self._create_session(curs, env, user, {})
        return response_ok(session_id=session.session_id)

    def _create_session(self, curs, env, user, sz_data):
        d = datetime.datetime.now(pytz.utc)
        data = {
            'session_id': '%s' % uuid4(),
            'environment_id': env.id,
            'user_id': user.id,
            'serialized_data': cjson.encode(sz_data),
            'start_date': d,
            'update_date': d,
        }
        session = Session(**data)
        mapping.save(curs, session)
        return session