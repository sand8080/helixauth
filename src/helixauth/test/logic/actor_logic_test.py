# must be imported first in helixauth set
from helixauth.test.logic.logic_test import LogicTestCase


class ActorLogicTestCase(LogicTestCase):
    def __init__(self, *args, **kwargs):
        super(ActorLogicTestCase, self).__init__(*args, **kwargs)
        self.actor_login = 'actor_test_login@h.com'
        self.actor_password = 'actor_test_password'
        self.actor_env_name = 'actor_test_env'

    def login_actor(self, bind_to_ip=False, fixed_lt_minutes=None):
        req = {'environment_name': self.actor_env_name,
            'email': self.actor_login, 'password': self.actor_password,
            'bind_to_ip': bind_to_ip}
        if fixed_lt_minutes is not None:
            req['fixed_lifetime_minutes'] = fixed_lt_minutes
        resp = self.login(**req)
        self.check_response_ok(resp)
        return resp['session_id']

    def create_actor_env(self):
        super(ActorLogicTestCase, self).setUp()
        req = {'name': self.actor_env_name, 'su_email': self.actor_login,
            'su_password': self.actor_password,
            'custom_actor_info': 'from %s' % self.actor_env_name}
        self.add_environment(**req)

    def get_users_info(self, sess_id, ids):
        req = {'session_id': sess_id, 'filter_params': {'ids': ids},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        return resp['users']

    def get_user_info(self, sess_id, email):
        req = {'session_id': sess_id, 'filter_params': {'email': email},
            'paging_params': {}}
        resp = self.get_users(**req)
        self.check_response_ok(resp)
        return resp['users'][0]

    def get_notifications_info(self, sess_id, ids=None, notif_type=None):
        f_params = {}
        if ids is not None:
            f_params['ids'] = ids
        if notif_type is not None:
            f_params['type'] = notif_type

        req = {'session_id': sess_id, 'filter_params': f_params,
            'paging_params': {}}
        resp = self.get_notifications(**req)
        self.check_response_ok(resp)
        return resp['notifications']

