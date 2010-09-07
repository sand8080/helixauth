from functools import partial

from helixcore import mapping
from helixcore import utils
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.db.wrapper import ObjectCreationError, SelectedMoreThanOneRow
from helixcore.misc import security
from helixcore.server.errors import (RequestProcessingError,
    ActionNotAllowedError, AuthError, DataIntegrityError)
from helixcore.server.response import response_ok

from helixauth.conf.db import transaction
from helixauth.error import EnvironmentNotFound, HelixauthError,\
    HelixauthObjectAlreadyExists
from helixauth.db.filters import EnvironmentFilter
from helixauth.db.dataobject import Environment, User
from helixauth.conf.log import logger
from helixauth.wsgi.protocol import protocol


#from helixauth.conf.db import transaction
#from helixauth.dataobject import Environment
#from helixauth.error import HelixauthError

#from helixcore.utils import filter_dict


def authentificate(method):
    @detalize_error(AuthError, RequestProcessingError.Category.auth, 'login')
    def decroated(self, data, curs):
        user = self.get_user(curs, data)
        data['user_id'] = user.id
        del data['login']
        del data['password']
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
        pass
#        return selector.get_auth_opertator(curs, data['login'], data['password'])

    @transaction()
    @detalize_error(HelixauthObjectAlreadyExists,
        RequestProcessingError.Category.data_integrity, 'name')
    def add_environment(self, data, curs=None):
        try:
            f = EnvironmentFilter(data, {}, {})
            env = f.filter_one_obj(curs)
            raise HelixauthObjectAlreadyExists('Environment "%s" already exist' % env.name)
        except EnvironmentNotFound, _:
            pass

        env_data = {'name': data.get('name')}
        env = Environment(**env_data)
        mapping.save(curs, env)

        u_data = {'environment_id': env.id, 'login': data.get('su_login'),
            'password': security.encrypt_password(data.get('su_password'))}
        user = User(**u_data)
        mapping.save(curs, user)

        return response_ok()