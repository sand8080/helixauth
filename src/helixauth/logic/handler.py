from functools import partial

from helixcore import mapping
from helixcore import security
from helixcore.actions.handler import detalize_error, AbstractHandler
from helixcore.error import DataIntegrityError
from helixcore.server.response import response_ok

from helixauth.conf.db import transaction
from helixauth.error import (EnvironmentNotFound,
    HelixauthObjectAlreadyExists, SessionNotFound, UserNotFound, SessionExpired,
    HelixauthError, UserInactive, ServiceDeactivationError, UserAuthError,
    GroupAlreadyExists, HelixauthObjectNotFound, UserWrongOldPassword,
    SuperUserCreationDenied, SuperUserModificationDenied)
from helixauth.db.filters import (EnvironmentFilter, UserFilter, ServiceFilter,
    SubjectUserFilter, GroupFilter, SessionFilter, ActionLogFilter)
from helixauth.db.dataobject import (Environment, User, Service,
    Group, serialize_field, deserialize_field)
from helixauth.logic.auth import Authentifier
from helixauth.wsgi.protocol import unauthorized_actions
import cjson
from helixcore.db.wrapper import ObjectCreationError
from functools import wraps


def _add_log_info(data, session, custom_actor_info=None):
    data['actor_user_id'] = session.user_id
    data['environment_id'] = session.environment_id
    data['session_id'] = session.session_id
    if custom_actor_info:
        data['custom_actor_info'] = custom_actor_info


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

        try:
            if user.environment_id != session.environment_id:
                raise HelixauthError('User and session from different environments')
            if not user.is_active:
                raise UserInactive()
            auth.check_access(session, Service.TYPE_AUTH, method.__name__)

            data.pop('session_id', None)
            custom_actor_info = data.pop('custom_actor_info', None)

            result = method(self, data, session, curs)
            _add_log_info(data, session, custom_actor_info)
            return result
        except Exception, e:
            _add_log_info(data, session)
            raise e
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

        # Required for proper logging action
        data['environment_id'] = env.id

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

        _add_log_info(data, session)

        return response_ok(session_id=session.session_id)

    @transaction()
    @detalize_error(HelixauthError, 'session_id')
    def logout(self, data, curs=None):

        session_id = data.get('session_id')
        f = SessionFilter({'session_id': session_id}, {}, {})
        try:
            session = f.filter_one_obj(curs, for_update=True)
            mapping.delete(curs, session)
            _add_log_info(data, session)
        except SessionNotFound:
            pass
        return response_ok()

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

        # adding groups of administrators and users
        d = {'environment_id': env.id, 'name': 'Administrators', 'is_active': True,
            'rights': [{'service_id': s.id, 'properties': actions}]}
        g = Group(**d)
        mapping.save(curs, g)
        d = {'environment_id': env.id, 'name': 'Users', 'is_active': True,
            'rights': [{'service_id': s.id, 'properties': ['modify_user_self',
            'get_user_rights', 'check_access', 'get_action_logs_self']}]}
        g = Group(**d)
        mapping.save(curs, g)

        # creating session for super user
        auth = Authentifier()
        session = auth.create_session(curs, env, user)

        _add_log_info(data, session)

        return response_ok(session_id=session.session_id,
            environment_id=env.id)

    @transaction()
    @authentificate
    def get_environment(self, data, session, curs=None):
        f = EnvironmentFilter({'id': session.environment_id}, {}, None)
        env = f.filter_one_obj(curs)
        return response_ok(environment=env.to_dict())

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

    def _filter_existed_groups(self, curs, session, groups_ids):
        f = GroupFilter(session.environment_id, {}, {}, None)
        groups = f.filter_objs(curs)
        g_ids = [g.id for g in groups]
        return filter(lambda x: x in g_ids, groups_ids)

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists, 'login')
    @detalize_error(SuperUserCreationDenied, 'role')
    def add_user(self, data, session, curs=None):
        a = Authentifier()
        env_id = session.environment_id
        u_data = {'environment_id': env_id, 'login': data.get('login'),
            'role': data.get('role', User.ROLE_USER),
            'password': a.encrypt_password(data.get('password')),
            'is_active': data.get('is_active', True),
        }
        if u_data['role'] == User.ROLE_SUPER:
            raise SuperUserCreationDenied

        groups_ids = data.get('groups_ids', [])
        filtered_g_ids = self._filter_existed_groups(curs, session, groups_ids)
        u_data['groups_ids'] = filtered_g_ids
        user = User(**u_data)
        try:
            mapping.save(curs, user)
        except ObjectCreationError:
            raise HelixauthObjectAlreadyExists

        # For correct action logging
        data['subject_users_ids'] = [user.id]
        return response_ok(id=user.id)

    @transaction()
    @authentificate
    def get_users(self, data, session, curs=None):
        f = UserFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        users, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('password')
            result.pop('environment_id')
            return result
        return response_ok(users=self.objects_info(users, viewer), total=total)

    @transaction()
    @authentificate
    @detalize_error(UserWrongOldPassword, 'old_password')
    def modify_user_self(self, data, session, curs=None):
        f = UserFilter(session, {'id': session.user_id}, {}, None)
        user = f.filter_one_obj(curs)
        old_password = data['old_password']
        a = Authentifier()
        if user.password != a.encrypt_password(old_password):
            raise UserWrongOldPassword()
        loader = partial(f.filter_one_obj, curs, for_update=True)
        d = {'new_password': a.encrypt_password(data['new_password'])}
        self.update_obj(curs, d, loader)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(SuperUserModificationDenied, 'subject_users_ids')
    @detalize_error(DataIntegrityError, 'ids')
    def modify_users(self, data, session, curs=None):
        f = UserFilter(session, {'roles': [User.ROLE_SUPER]}, {}, None)
        su = f.filter_one_obj(curs)
        u_ids = data['ids']
        if su.id in u_ids:
            raise SuperUserModificationDenied()
        groups_ids = data.get('new_groups_ids', [])
        filtered_g_ids = self._filter_existed_groups(curs, session, groups_ids)
        data['new_groups_ids'] = filtered_g_ids

        f = UserFilter(session, {'ids': u_ids}, {}, 'id')
        loader = partial(f.filter_objs, curs, for_update=True)
        self.update_objs(curs, data, loader)
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(ObjectCreationError, 'type')
    def add_service(self, data, session, curs=None):
        d = dict(data)
        d['environment_id'] = session.environment_id
        d['is_possible_deactiate'] = True
        s = Service(**d)
        try:
            mapping.save(curs, s)
        except ObjectCreationError:
            raise HelixauthObjectAlreadyExists
        return response_ok(id=s.id)

    @transaction()
    @authentificate
    def get_services(self, data, session, curs=None):
        f = ServiceFilter(session.environment_id, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ss, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result = deserialize_field(result, 'serialized_properties', 'properties')
            result.pop('environment_id')
            return result
        return response_ok(services=self.objects_info(ss, viewer),
            total=total)

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectAlreadyExists, 'new_name')
    @detalize_error(ServiceDeactivationError, 'new_is_active')
    def modify_service(self, data, session, curs=None):
        f = ServiceFilter(session.environment_id, data, {}, None)

        # checking service deactivation is possible
        srv = f.filter_one_obj(curs)
        if not data.get('new_is_active', True) and not srv.is_possible_deactiate:
            raise ServiceDeactivationError(srv.name)

        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            d = serialize_field(data, 'new_properties', 'new_serialized_properties')
            self.update_obj(curs, d, loader)
        except DataIntegrityError:
            raise HelixauthObjectAlreadyExists('Service %s already exists' %
                data.get('new_name'))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(GroupAlreadyExists, 'name')
    def add_group(self, data, session, curs=None):
        group = Group(**data)
        group.environment_id = session.environment_id
        try:
            mapping.save(curs, group)
        except ObjectCreationError:
            raise GroupAlreadyExists('Group %s already exists' % group.name)
        return response_ok(id=group.id)

    @transaction()
    @authentificate
    @detalize_error(GroupAlreadyExists, 'name')
    def modify_group(self, data, session, curs=None):
        f = GroupFilter(session.environment_id, {'id': data.get('id')}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            self.update_obj(curs, serialize_field(data, 'new_rights', 'new_serialized_rights'),
                loader)
        except DataIntegrityError:
            raise GroupAlreadyExists(data.get('new_name'))
        return response_ok()

    @transaction()
    @authentificate
    @detalize_error(HelixauthObjectNotFound, 'id')
    def delete_group(self, data, session, curs=None):
        f = GroupFilter(session.environment_id, {'id': data.get('id')}, {}, None)
        mapping.delete(curs, f.filter_one_obj(curs))
        return response_ok()

    @transaction()
    @authentificate
    def get_groups(self, data, session, curs=None):
        f = GroupFilter(session.environment_id, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ss, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id', None)
            s_rights = result.pop('serialized_rights', '')
            result['rights'] = cjson.decode(s_rights)
            return result
        return response_ok(groups=self.objects_info(ss, viewer),
            total=total)

    @transaction()
    @authentificate
    def get_action_logs(self, data, session, curs=None):
        return self._get_action_logs(data, session, curs)

    def _get_action_logs(self, data, session, curs):
        f_params = data['filter_params']
        u_id = f_params.pop('user_id', None)
        if u_id:
            f_params[('subject_users_ids', 'actor_user_id')] = (u_id, u_id)
        f = ActionLogFilter(session.environment_id, f_params,
            data['paging_params'], data.get('ordering_params'))
        ss, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id', None)
            result['request_date'] = '%s' % result['request_date']
            return result
        return response_ok(action_logs=self.objects_info(ss, viewer),
            total=total)

    @transaction()
    @authentificate
    def get_action_logs_self(self, data, session, curs=None):
        data['filter_params']['user_id'] = session.user_id
        return self._get_action_logs(data, session, curs)

    @transaction()
    @authentificate
    @detalize_error(UserAuthError, [])
    def get_user_rights(self, data, session, curs=None):
        s_data = cjson.decode(session.serialized_data)
        s_rights = s_data['rights']
        srvs_id_type_idx = s_data['services_id_type_idx']
        rights = []
        for srv_id in srvs_id_type_idx.keys():
            srv_type = srvs_id_type_idx[srv_id]
            props = s_rights[srv_type]
            rights.append({'service_id': int(srv_id),
                'service_type': srv_type, 'properties': props})
        return response_ok(rights=rights)

    @transaction()
    @authentificate
    @detalize_error(UserAuthError, [])
    def check_access(self, data, session, curs=None):
        a = Authentifier()
        srv_type = data.get('service_type', None)
        p = data.get('property', None)
        a.check_access(session, srv_type, p)
        return response_ok()
