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
