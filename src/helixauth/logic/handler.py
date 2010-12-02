from functools import partial

from helixcore import mapping
from helixcore import security
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.error import DataIntegrityError
from helixcore.server.response import response_ok

from helixauth.conf.db import transaction
from helixauth.error import (EnvironmentNotFound,
    HelixauthObjectAlreadyExists, SessionNotFound, UserNotFound, SessionExpired,
    HelixauthError, UserInactive, ServiceDeactivationError, UserAuthError,)
from helixauth.db.filters import (EnvironmentFilter, UserFilter, ServiceFilter,
    UserRightsFilter, SessionFilter, SubjectUserFilter)
from helixauth.db.dataobject import Environment, User, Service, UserRights
from helixauth.logic.auth import Authentifier
from helixauth.wsgi.protocol import unauthorized_actions
import cjson
from helixcore.db.wrapper import ObjectCreationError
from functools import wraps


def authentificate(method):
    @wraps(method)
    @detalize_error(SessionNotFound, 'session_id')
    @detalize_error(SessionExpired, 'session_id')
    @detalize_error(HelixauthError, 'session_id')
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

        auth.check_access(session, Service.TYPE_AUTH, method.__name__)
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
        a = Authentifier()
        actions = a.get_auth_api_actions()
        return response_ok(actions=actions)

    def get_authorized_api_actions(self, data):
        resp = self.get_api_actions(data)
        a = resp['actions']
        auth_a = filter(lambda x: x not in unauthorized_actions, a)
        return response_ok(actions=auth_a)

    @transaction()
    @detalize_error(EnvironmentNotFound, 'environment_name')
    @detalize_error(UserAuthError, ['login', 'password'])
    @detalize_error(UserInactive, ['login', 'password'])
    def login(self, data, curs=None):
        a = Authentifier()
        enc_data = security.encrypt_passwords(data, a.encrypt_password)
        f = EnvironmentFilter(enc_data, {}, {})
        env = f.filter_one_obj(curs)

        f = SubjectUserFilter(env.id, enc_data, {}, {})
        try:
            user = f.filter_one_obj(curs)
        except UserNotFound:
            raise UserAuthError
        if not user.is_active:
            raise UserInactive()

        # creating session
        auth = Authentifier()
        session = auth.create_session(curs, env, user)

        # Required for proper logging action
        data['environment_id'] = env.id
        data['actor_user_id'] = user.id

        return response_ok(session_id=session.session_id)

    @transaction()
    @detalize_error(HelixauthObjectAlreadyExists, ['name', 'su_login', 'su_password'])
    def add_environment(self, data, curs=None):
        env_data = {'name': data.get('name')}
        env = Environment(**env_data)
        try:
            mapping.save(curs, env)
        except ObjectCreationError:
            raise HelixauthObjectAlreadyExists('Environment %s already exists' % env.name)

        # creating user
        a = Authentifier()
        u_data = {'environment_id': env.id, 'login': data.get('su_login'),
            'password': a.encrypt_password(data.get('su_password')),
            'role': User.ROLE_SUPER}
        user = User(**u_data)
        mapping.save(curs, user)


        # adding default service auth
        a_data = self.get_authorized_api_actions({})
        actions = a_data['actions']
        d = {'environment_id': env.id, 'name': 'Auth',
            'type': Service.TYPE_AUTH, 'is_active': True,
            'is_possible_deactiate': False, 'properties': actions}
        s = Service(**d)
        mapping.save(curs, s)

        auth = Authentifier()
        session = auth.create_session(curs, env, user)

        # Required for proper logging action
        data['actor_user_id'] = session.user_id
        data['environment_id'] = session.environment_id

        return response_ok(session_id=session.session_id,
            environment_id=env.id)

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists, 'new_name')
    def modify_environment(self, data, session, curs=None):
        f = EnvironmentFilter({'id': session.environment_id}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            self.update_obj(curs, data, loader)
        except DataIntegrityError:
            raise HelixauthObjectAlreadyExists('Environment %s already exists' %
                data.get('new_name'))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists, 'login')
    def add_user(self, data, session, curs=None):
        a = Authentifier()
        u_data = {'environment_id': session.environment_id,
            'login': data.get('login'), 'role': data.get('role', User.ROLE_USER),
            'password': a.encrypt_password(data.get('password')),
            'is_active': data.get('is_active', True),
        }
        user = User(**u_data)
        mapping.save(curs, user)
        # For correct action logging
        data['subject_users_ids'] = [user.id]
        return response_ok(user_id=user.id)

    @transaction()
    @authentificate
    @detalize_error(ObjectCreationError, 'name')
    def add_service(self, data, session, curs=None):
        d = dict(data)
        d['environment_id'] = session.environment_id
        d['is_possible_deactiate'] = True
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

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists, 'new_name')
    @detalize_error(ServiceDeactivationError, 'new_is_active')
    def modify_service(self, data, session, curs=None):
        f = ServiceFilter(session.environment_id, {'id': data['service_id']},
            {}, None)

        # checking service deactivation is possible
        srv = f.filter_one_obj(curs)
        if not data.get('new_is_active', True) and not srv.is_possible_deactiate:
            raise ServiceDeactivationError(srv.name)

        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            self.update_obj(curs, data, loader)
        except DataIntegrityError:
            raise HelixauthObjectAlreadyExists('Service %s already exists' %
                data.get('new_name'))
        return response_ok()

    @transaction()
    @authentificate
    def modify_users_rights(self, data, session, curs=None):
        u_ids = data['subject_users_ids']
        f = UserRightsFilter(session.environment_id,
            {'subject_users_ids': u_ids}, {}, ['id'])
        u_rs = f.filter_objs(curs, for_update=True)
        u_rs_idx = dict([(r.user_id, r) for r in u_rs])

        # Filtering services from environment
        f = ServiceFilter(session.environment_id, {}, {}, None)
        ss_idx = f.indexed_by_id(curs)
        rights = filter(lambda x: x['service_id'] in ss_idx, data['rights'])

        for u_id in u_ids:
            if u_id in u_rs_idx:
                r = u_rs_idx[u_id]
            else:
                r = UserRights(**{'environment_id': session.environment_id,
                    'user_id': u_id})
            r.serialized_rights = cjson.encode(rights)
            mapping.save(curs, r)

        # invalidate users sessions data
        f = SessionFilter({'environment_id': session.environment_id,
            'subject_users_ids': u_ids}, {}, ['id'])
        sess = f.filter_objs(curs, for_update=True)
        mapping.delete_objects(curs, sess)

        return response_ok()

    @transaction()
    @detalize_error(UserAuthError, [])
    def check_access(self, data, session, curs=None):
        a = Authentifier()
        srv_type = data.get('service_type', None)
        p = data.get('property', None)
        a.check_access(session, srv_type, p)
        return response_ok()
