from functools import partial

from helixcore import mapping
from helixcore import security
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.server.errors import RequestProcessingError
from helixcore.server.response import response_ok

from helixauth.conf.db import transaction
from helixauth.error import (EnvironmentNotFound,
    HelixauthObjectAlreadyExists, SessionNotFound, UserNotFound, SessionExpired,
    HelixauthError, UserInactive)
from helixauth.db.filters import EnvironmentFilter, UserFilter, ServiceFilter
from helixauth.db.dataobject import Environment, User, Service
from helixauth.logic.auth import Authentifier
from helixauth.wsgi.protocol import protocol


def authentificate(method):
    @detalize_error(SessionNotFound, RequestProcessingError.Category.auth, 'session_id')
    @detalize_error(SessionExpired, RequestProcessingError.Category.auth, 'session_id')
    @detalize_error(HelixauthError, RequestProcessingError.Category.auth, 'session_id')
    def decroated(self, data, curs):
        auth = Authentifier()
        session_id = data.get('session_id')
        session = auth.get_session(session_id)

        f = UserFilter(session, {'id': session.user_id}, {}, {})
        user = f.filter_one_obj(curs)

        if user.environment_id != session.environment_id:
            raise HelixauthError('User and session from different environments')
        if not user.is_active:
            raise UserInactive()

        auth.check_access(session, user, method)
        data.pop('session_id', None)
        custom_actor_info = data.pop('custom_actor_info', None)

        result = method(self, data, session, curs)

        # Required for proper logging action
        data['actor_user_id'] = session.user_id
        data['environment_id'] = session.environment_id
        data['custom_actor_info'] = custom_actor_info

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
    @detalize_error(EnvironmentNotFound,
        RequestProcessingError.Category.auth, 'login')
    @detalize_error(UserNotFound,
        RequestProcessingError.Category.auth, 'login')
    @detalize_error(UserInactive,
        RequestProcessingError.Category.auth, 'login')
    def login(self, data, curs=None):
        a = Authentifier()
        enc_data = security.encrypt_passwords(data, a.encrypt_password)
        f = EnvironmentFilter(enc_data, {}, {})
        env = f.filter_one_obj(curs)

        # Required for proper logging action
        data['environment_id'] = env.id

        class SessionImitator(object):
            def __init__(self):
                self.environment_id = env.id

        f = UserFilter(SessionImitator(), enc_data, {}, {})
        user = f.filter_one_obj(curs)
        if not user.is_active:
            raise UserInactive()

        # Required for proper logging action
        data['actor_user_id'] = user.id

        # creating session
        auth = Authentifier()
        session = auth.create_session(curs, env, user)

        return response_ok(session_id=session.session_id)

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
        a = Authentifier()
        u_data = {'environment_id': env.id, 'login': data.get('su_login'),
            'password': a.encrypt_password(data.get('su_password')),
            'role': User.ROLE_SUPER}
        user = User(**u_data)
        mapping.save(curs, user)

        auth = Authentifier()
        session = auth.create_session(curs, env, user)

        # Required for proper logging action
        data['actor_user_id'] = session.user_id
        data['environment_id'] = session.environment_id

        return response_ok(session_id=session.session_id,
            environment_id=env.id)

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists,
        RequestProcessingError.Category.data_integrity, 'new_name')
    def modify_environment(self, data, session, curs=None):
        f = EnvironmentFilter({'id': session.environment_id}, {}, {})
        loader = partial(f.filter_one_obj, curs, for_update=True)
        self.update_obj(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists,
        RequestProcessingError.Category.data_integrity, 'login')
    def add_user(self, data, session, curs=None):
        a = Authentifier()
        u_data = {'environment_id': session.environment_id,
            'login': data.get('login'), 'role': data.get('role'),
            'password': a.encrypt_password(data.get('password')),
            'is_active': data.get('is_active', True),
        }
        user = User(**u_data)
        mapping.save(curs, user)
        # For correct action logging
        data['subject_user_ids'] = [user.id]
        return response_ok(user_id=user.id)

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists,
        RequestProcessingError.Category.data_integrity, 'name')
    def add_service(self, data, session, curs=None):
        d = {'environment_id': session.environment_id,
            'name': data.get('name'), 'is_possible_deactiate': True,
            'is_active': data.get('is_active', True),
            'properties': data.get('properties')
        }
        s = Service(**d)
        mapping.save(curs, s)
        return response_ok(service_id=s.id)

    @transaction()
    @authentificate
    def get_services(self, data, session, curs=None):
        f = ServiceFilter(session.environment_id, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ss, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id', None)
            return result
        return response_ok(services=self.objects_info(ss, viewer),
            total=total)

