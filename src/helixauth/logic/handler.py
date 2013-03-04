import json
from functools import partial
from functools import wraps

from helixcore import mapping
from helixcore.actions.handler import (detalize_error, AbstractHandler,
    set_subject_users_ids, execution_time)
from helixcore.db.wrapper import ObjectCreationError
from helixcore.error import DataIntegrityError
from helixcore.json_validator.html_transformer import HtmlTransformer
from helixcore.server.response import response_ok

from helixauth.conf.db import transaction
from helixauth.error import (EnvironmentNotFound,
    HelixauthObjectAlreadyExists, SessionNotFound, UserNotFound, SessionExpired,
    HelixauthError, UserInactive, ServiceDeactivationError, UserAuthError,
    GroupAlreadyExists, HelixauthObjectNotFound, UserWrongOldPassword,
    SuperUserCreationDenied, SuperUserModificationDenied, UserAccessDenied,
    ServiceDeletionError, ServiceNotFound, SessionIpChanged,
    SessionTooLargeFixedLifetime, UserNewPasswordNotSet)
from helixauth.db.filters import (EnvironmentFilter, UserFilter, ServiceFilter,
    SubjectUserFilter, GroupFilter, SessionFilter, ActionLogFilter,
    NotificatonFilter)
from helixauth.db.dataobject import (Environment, User, Service,
    Group, Notification)
from helixauth.logic.auth import Authenticator
from helixauth.wsgi.protocol import unauthorized_actions, protocol
from helixauth.logic import message
from helixauth.logic.notifier import Notifier


def _add_log_info(data, session, custom_actor_info=None):
    data['actor_user_id'] = session.user_id
    data['environment_id'] = session.environment_id
    data['session_id'] = session.session_id
    if custom_actor_info:
        data['custom_actor_info'] = custom_actor_info


def authenticate(method):
    @wraps(method)
    @detalize_error(SessionNotFound, 'session_id')
    @detalize_error(SessionExpired, 'session_id')
    @detalize_error(HelixauthError, 'session_id')
    def decroated(self, data, req_info, curs):
        auth = Authenticator()
        session_id = data.get('session_id')
        session = auth.get_session(session_id)

        f = UserFilter(session, {'id': session.user_id}, {}, {})
        user = f.filter_one_obj(curs)

        try:
            if user.environment_id != session.environment_id:
                raise HelixauthError('User and session from different environments')
            if not user.is_active:
                raise UserInactive()
            auth.check_access(session, Service.TYPE_AUTH, method.__name__, req_info)

            data.pop('session_id', None)
            custom_actor_info = data.pop('custom_actor_info', None)

            try:
                result = method(self, data, req_info, session, curs)
            except Exception, e:
                data['environment_id'] = session.environment_id
                _add_log_info(data, session, custom_actor_info)
                raise e

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
    @execution_time
    def ping(self, data, req_info): #IGNORE:W0613
        return response_ok()

    @execution_time
    def get_api_actions(self, data, req_info):
        a = Authenticator()
        actions = a.get_auth_api_actions()
        return response_ok(actions=actions)

    @execution_time
    def get_authorized_api_actions(self, data, req_info):
        resp = self.get_api_actions(data, req_info)
        a = resp['actions']
        auth_a = filter(lambda x: x not in unauthorized_actions, a)
        return response_ok(actions=auth_a)

    @execution_time
    @transaction()
    @authenticate
    def get_api_scheme(self, data, req_info, session, curs=None):
        trans = HtmlTransformer()
        return response_ok(scheme=trans.process_protocol(protocol))

    @execution_time
    @transaction()
    @detalize_error(EnvironmentNotFound, 'environment_name')
    @detalize_error(UserAuthError, ['email', 'password'])
    @detalize_error(UserInactive, ['email', 'password'])
    @detalize_error(SessionTooLargeFixedLifetime, 'fixed_lifetime_minutes')
    def login(self, data, req_info, curs=None):
        f = EnvironmentFilter(data, {}, None)
        env = f.filter_one_obj(curs)

        # Required for proper logging action
        data['environment_id'] = env.id

        f_params = {'environment_id': env.id, 'email': data.get('email')}
        f = SubjectUserFilter(env.id, f_params, {}, None)
        try:
            user = f.filter_one_obj(curs)
        except UserNotFound:
            raise UserAuthError
        if not user.is_active:
            raise UserInactive()

        # checking password
        auth = Authenticator()
        enc_p = auth.encrypt_password(data.get('password'), user.salt)
        if enc_p != user.password:
            raise UserAuthError

        # creating session
        bind_to_ip = data.get('bind_to_ip', False)
        lt_minutes = data.get('fixed_lifetime_minutes')
        session = auth.create_session(curs, env, user, req_info,
            bind_to_ip=bind_to_ip, lifetime_minutes=lt_minutes)

        _add_log_info(data, session)

        return response_ok(session_id=session.session_id,
            user_id=session.user_id, environment_id=session.environment_id)

    @execution_time
    @transaction()
    @detalize_error(HelixauthError, 'session_id')
    def logout(self, data, req_info, curs=None):

        session_id = data.get('session_id')
        f = SessionFilter({'session_id': session_id}, {}, None)
        try:
            session = f.filter_one_obj(curs, for_update=True)
            mapping.delete(curs, session)
            _add_log_info(data, session)
        except SessionNotFound:
            pass
        return response_ok()

    def _create_default_services(self, req_info, curs, env):
        # adding default service auth
        a_data = self.get_authorized_api_actions({}, req_info)
        actions_auth = a_data['actions']
        d = {'environment_id': env.id, 'name': 'Auth',
            'type': Service.TYPE_AUTH, 'is_active': True,
            'is_possible_deactiate': False, 'properties': actions_auth}
        s_auth = Service(**d)
        mapping.save(curs, s_auth)

        # adding default service billing
        actions_billing = ['get_currencies', 'get_used_currencies', 'modify_used_currencies',
            'get_action_logs', 'get_action_logs_self',
            'add_balance', 'get_balances', 'get_balances_self', 'modify_balances',
            'add_receipt', 'add_bonus', 'lock', 'unlock', 'charge_off',
            'get_locks', 'get_locks_self',
            'get_transactions', 'get_transactions_self']
        d = {'environment_id': env.id, 'name': 'Billing',
            'type': Service.TYPE_BILLING, 'is_active': True,
            'is_possible_deactiate': True, 'properties': actions_billing}
        s_billing = Service(**d)
        mapping.save(curs, s_billing)

        # adding default service tariff
        actions_tariff = ['add_tariffication_object', 'modify_tariffication_object',
            'delete_tariffication_object', 'get_tariffication_objects',
            'add_tariff', 'modify_tariff', 'delete_tariff', 'get_tariffs',
            'save_rule', 'delete_rule', 'apply_draft_rules',
            'get_tariffs_prices', 'get_price', 'get_draft_price',
            'add_user_tariff', 'delete_user_tariff', 'get_user_tariffs']
        d = {'environment_id': env.id, 'name': 'Tariff',
            'type': Service.TYPE_TARIFF, 'is_active': True,
            'is_possible_deactiate': True, 'properties': actions_tariff}
        s_tariff = Service(**d)
        mapping.save(curs, s_tariff)

        # adding groups of administrators and users
        d = {'environment_id': env.id, 'name': 'Administrators', 'is_active': True,
            'rights': [
                {'service_id': s_auth.id, 'properties': actions_auth},
                {'service_id': s_billing.id, 'properties': []}
            ]}
        g = Group(**d)
        mapping.save(curs, g)

        d = {'environment_id': env.id, 'name': 'Billing Administrators', 'is_active': True,
            'rights': [
                {'service_id': s_auth.id, 'properties': ['check_user_exist']},
                {'service_id': s_billing.id, 'properties': actions_billing}
            ]}
        g = Group(**d)
        mapping.save(curs, g)

        d = {'environment_id': env.id, 'name': 'Tariff Administrators', 'is_active': True,
            'rights': [
                {'service_id': s_auth.id, 'properties': ['check_user_exist']},
                {'service_id': s_tariff.id, 'properties': actions_tariff}
            ]}
        g = Group(**d)
        mapping.save(curs, g)

        d = {'environment_id': env.id, 'name': 'Users', 'is_active': True,
            'rights': [
                {'service_id': s_auth.id, 'properties': ['modify_user_self',
                    'get_user_rights', 'check_access', 'get_action_logs_self']},
                {'service_id': s_billing.id, 'properties': []},
            ]}
        g = Group(**d)
        mapping.save(curs, g)

        d = {'environment_id': env.id, 'name': 'Billing Users', 'is_active': True,
            'rights': [
                {'service_id': s_auth.id, 'properties': []},
                {'service_id': s_billing.id, 'properties': [
                    'get_action_logs_self', 'get_balances_self',
                    'get_locks_self', 'get_transactions_self']},
            ]}
        g = Group(**d)
        mapping.save(curs, g)

    def _create_default_notifications(self, curs, env):
        notifier = Notifier()
        for event in message.EVENTS:
            e_msgs = notifier.default_email_notif_struct(event)
            n = Notification(environment_id=env.id, event=event,
                is_active=True, type=Notification.TYPE_EMAIL,
                messages=e_msgs)
            mapping.save(curs, n)

    def _create_default_objects(self, req_info, curs, env):
        self._create_default_services(req_info, curs, env)
        self._create_default_notifications(curs, env)

    @execution_time
    @transaction()
    @detalize_error(HelixauthObjectAlreadyExists, ['name', 'su_email', 'su_password'])
    def add_environment(self, data, req_info, curs=None):
        env_data = {'name': data.get('name')}
        env = Environment(**env_data)
        try:
            mapping.save(curs, env)
        except ObjectCreationError:
            raise HelixauthObjectAlreadyExists('Environment %s already exists' % env.name)

        # creating user
        a = Authenticator()
        salt = a.salt()
        u_data = {'environment_id': env.id, 'email': data.get('su_email'),
            'password': a.encrypt_password(data.get('su_password'), salt),
            'salt': salt, 'role': User.ROLE_SUPER,
            'lang': User.DEFAULT_LANG}
        user = User(**u_data)
        mapping.save(curs, user)

        # creating default services and groups
        self._create_default_objects(req_info, curs, env)

        # creating session for super user
        auth = Authenticator()
        session = auth.create_session(curs, env, user, req_info)

        _add_log_info(data, session)

        return response_ok(session_id=session.session_id,
            environment_id=env.id, user_id=session.user_id)

    @execution_time
    @transaction()
    @authenticate
    def get_environment(self, data, req_info, session, curs=None):
        f = EnvironmentFilter({'id': session.environment_id}, {}, None)
        env = f.filter_one_obj(curs)
        return response_ok(environment=env.to_dict())

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(HelixauthObjectAlreadyExists, 'new_name')
    def modify_environment(self, data, req_info, session, curs=None):
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

    @execution_time
    @set_subject_users_ids('id')
    @transaction()
    @authenticate
    @detalize_error(HelixauthObjectAlreadyExists, 'email')
    @detalize_error(SuperUserCreationDenied, 'role')
    def add_user(self, data, req_info, session, curs=None):
        a = Authenticator()
        env_id = session.environment_id
        salt = a.salt()
        u_data = {'environment_id': env_id, 'email': data.get('email'),
            'role': data.get('role', User.ROLE_USER),
            'password': a.encrypt_password(data.get('password'), salt),
            'salt': salt, 'is_active': data.get('is_active', True),
            'lang': data.get('lang', User.DEFAULT_LANG)
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
        data['id'] = [user.id]
        n = Notifier()
        n_process = n.register_user(user, session)
        return response_ok(id=user.id, notification=n_process)

    @execution_time
    @transaction()
    @authenticate
    def get_users(self, data, req_info, session, curs=None):
        f = UserFilter(session, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        users, total = f.filter_counted(curs)

        f = GroupFilter(session.environment_id, {}, {}, None)
        groups = f.filter_objs(curs)
        g_ids = [g.id for g in groups]

        def viewer(obj):
            result = obj.to_dict()
            result.pop('password')
            result.pop('salt')
            result.pop('environment_id')
            result['groups_ids'] = filter(lambda x: x in g_ids, result['groups_ids'])
            return result
        return response_ok(users=self.objects_info(users, viewer), total=total)

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(UserWrongOldPassword, 'old_password')
    @detalize_error(UserNewPasswordNotSet, 'new_password')
    def modify_user_self(self, data, req_info, session, curs=None):
        f = UserFilter(session, {'id': session.user_id}, {}, None)
        user = f.filter_one_obj(curs)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        d = {}
        if 'new_lang' in data:
            d['new_lang'] = data['new_lang']
        if old_password is not None:
            if new_password is None or len(new_password) == 0:
                raise UserNewPasswordNotSet("Empty new password can't be set")
            a = Authenticator()
            if user.password != a.encrypt_password(old_password, user.salt):
                raise UserWrongOldPassword()
            salt = a.salt()
            d['new_salt'] = salt
            d['new_password'] = a.encrypt_password(data['new_password'], salt)
        loader = partial(f.filter_one_obj, curs, for_update=True)
        self.update_obj(curs, d, loader)
        return response_ok()

    @execution_time
    @set_subject_users_ids('ids')
    @transaction()
    @authenticate
    @detalize_error(SuperUserModificationDenied, 'subject_users_ids')
    @detalize_error(DataIntegrityError, 'ids')
    def modify_users(self, data, req_info, session, curs=None):
        u_ids = data['ids']
        f = UserFilter(session, {'roles': [User.ROLE_SUPER]}, {}, None)
        su = f.filter_one_obj(curs)
        if su.id in u_ids:
            raise SuperUserModificationDenied()
        groups_ids = data.get('new_groups_ids', [])
        filtered_g_ids = self._filter_existed_groups(curs, session, groups_ids)
        data['new_groups_ids'] = filtered_g_ids
        if 'new_password' in data:
            a = Authenticator()
            salt = a.salt()
            data['new_password'] = a.encrypt_password(data['new_password'], salt)
            data['new_salt'] = salt
        f = UserFilter(session, {'ids': u_ids}, {}, None)
        loader = partial(f.filter_objs, curs, for_update=True)
        self.update_objs(curs, data, loader)
        return response_ok()

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(ObjectCreationError, 'type')
    def add_service(self, data, req_info, session, curs=None):
        d = dict(data)
        d['environment_id'] = session.environment_id
        d['is_possible_deactiate'] = True
        s = Service(**d)
        try:
            mapping.save(curs, s)
        except ObjectCreationError:
            raise HelixauthObjectAlreadyExists
        return response_ok(id=s.id)

    @execution_time
    @transaction()
    @authenticate
    def get_services(self, data, req_info, session, curs=None):
        f = ServiceFilter(session.environment_id, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ss, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result = mapping.objects.deserialize_field(result, 'serialized_properties', 'properties')
            result.pop('environment_id')
            return result
        return response_ok(services=self.objects_info(ss, viewer),
            total=total)

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(HelixauthObjectAlreadyExists, 'new_name')
    @detalize_error(ServiceDeactivationError, 'new_is_active')
    def modify_service(self, data, req_info, session, curs=None):
        f = ServiceFilter(session.environment_id, data, {}, None)

        # checking service deactivation is possible
        srv = f.filter_one_obj(curs)
        if not data.get('new_is_active', True) and not srv.is_possible_deactiate:
            raise ServiceDeactivationError(srv.name)

        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            d = mapping.objects.serialize_field(data, 'new_properties', 'new_serialized_properties')
            self.update_obj(curs, d, loader)
        except DataIntegrityError:
            raise HelixauthObjectAlreadyExists('Service %s already exists' %
                data.get('new_name'))
        return response_ok()

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(ServiceNotFound, 'id')
    @detalize_error(ServiceDeletionError, 'id')
    def delete_service(self, data, req_info, session, curs=None):
        f = ServiceFilter(session.environment_id, {'id': data.get('id')}, {}, None)
        s = f.filter_one_obj(curs)
        if s.type == Service.TYPE_AUTH:
            raise ServiceDeletionError(Service.TYPE_AUTH)
        mapping.delete(curs, s)
        return response_ok()

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(GroupAlreadyExists, 'name')
    def add_group(self, data, req_info, session, curs=None):
        group = Group(**data)
        group.environment_id = session.environment_id
        try:
            mapping.save(curs, group)
        except ObjectCreationError:
            raise GroupAlreadyExists('Group %s already exists' % group.name)
        return response_ok(id=group.id)

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(GroupAlreadyExists, 'name')
    def modify_group(self, data, req_info, session, curs=None):
        f = GroupFilter(session.environment_id, {'id': data.get('id')}, {}, None)
        loader = partial(f.filter_one_obj, curs, for_update=True)
        try:
            self.update_obj(curs, mapping.objects.serialize_field(data, 'new_rights', 'new_serialized_rights'),
                loader)
        except DataIntegrityError:
            raise GroupAlreadyExists(data.get('new_name'))
        return response_ok()

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(HelixauthObjectNotFound, 'id')
    def delete_group(self, data, req_info, session, curs=None):
        f = GroupFilter(session.environment_id, {'id': data.get('id')}, {}, None)
        mapping.delete(curs, f.filter_one_obj(curs))
        return response_ok()

    @execution_time
    @transaction()
    @authenticate
    def get_groups(self, data, req_info, session, curs=None):
        f = GroupFilter(session.environment_id, data['filter_params'],
            data['paging_params'], data.get('ordering_params'))
        ss, total = f.filter_counted(curs)
        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id', None)
            s_rights = result.pop('serialized_rights', '')
            result['rights'] = json.loads(s_rights)
            return result
        return response_ok(groups=self.objects_info(ss, viewer),
            total=total)

    @execution_time
    @transaction()
    @authenticate
    def get_action_logs(self, data, req_info, session, curs=None):
        return self._get_action_logs(data, session, curs)

    @execution_time
    @transaction()
    @authenticate
    def get_action_logs_self(self, data, req_info, session, curs=None):
        data['filter_params']['user_id'] = session.user_id
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

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(UserAuthError, [])
    def get_user_rights(self, data, req_info, session, curs=None):
        s_data = json.loads(session.serialized_data)
        s_rights = s_data['rights']
        srvs_id_type_idx = s_data['services_id_type_idx']
        rights = []
        for srv_id in srvs_id_type_idx.keys():
            srv_type = srvs_id_type_idx[srv_id]
            props = s_rights[srv_type]
            rights.append({'service_id': int(srv_id),
                'service_type': srv_type, 'properties': props})
        return response_ok(rights=rights)

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(UserAuthError, [])
    def check_access(self, data, req_info, session, curs=None):
        a = Authenticator()
        srv_type = data.get('service_type', None)
        p = data.get('property', None)
        try:
            a.check_access(session, srv_type, p, req_info)
            return response_ok(user_id=session.user_id,
                environment_id=session.environment_id, access='granted')
        except (UserAccessDenied, SessionIpChanged):
            return response_ok(user_id=session.user_id,
                environment_id=session.environment_id, access='denied')

    @execution_time
    @transaction()
    @authenticate
    def check_user_exist(self, data, req_info, session, curs=None):
        f = UserFilter(session, {'id': data['id']}, {}, None)
        exist = False
        try:
            f.filter_one_obj(curs)
            exist = True
        except UserNotFound:
            pass
        return response_ok(exist=exist)

    @execution_time
    @transaction()
    @authenticate
    def get_notifications(self, data, req_info, session, curs=None):
        f = NotificatonFilter(session.environment_id,
            data['filter_params'], data['paging_params'],
            data.get('ordering_params'))
        notifs, total = f.filter_counted(curs)

        def viewer(obj):
            result = obj.to_dict()
            result.pop('environment_id')
            result = mapping.objects.deserialize_field(result,
                'serialized_messages', 'messages')
            return result
        return response_ok(notifications=self.objects_info(notifs, viewer), total=total)

    @execution_time
    @transaction()
    @authenticate
    @detalize_error(DataIntegrityError, 'ids')
    def modify_notifications(self, data, req_info, session, curs=None):
        n_ids = data['ids']
        f = NotificatonFilter(session.environment_id, {'ids': n_ids},
            {}, None)
        loader = partial(f.filter_objs, curs, for_update=True)
        self.update_objs(curs, data, loader)
        return response_ok()

