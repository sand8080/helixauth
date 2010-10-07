# must be imported first in helixauth set
from helixauth.test.logic.logic_test import LogicTestCase


class ActorLogicTestCase(LogicTestCase):
    def __init__(self, *args, **kwargs):
        super(ActorLogicTestCase, self).__init__(*args, **kwargs)
        self.actor_login = 'actor_test_login'
        self.actor_password = 'actor_test_password'
        self.actor_env_name = 'actor_test_env'

    def login_actor(self):
        req = {'environment_name': self.actor_env_name,
            'login': self.actor_login, 'password': self.actor_password}
        return self.login(**req)

    def create_actor_env(self):
        super(ActorLogicTestCase, self).setUp()
        req = {'name': self.actor_env_name, 'su_login': self.actor_login,
            'su_password': self.actor_password,
            'custom_actor_info': 'from %s' % self.actor_env_name}
        self.add_environment(**req)
