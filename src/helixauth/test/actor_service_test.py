# must be imported first in helixauth set
from helixauth.test.service_test import ServiceTestCase


class ActorServiceTest(ServiceTestCase):
    def __init__(self, *args, **kwargs):
        super(ActorServiceTest, self).__init__(*args, **kwargs)
        self.actor_login = 'actor_test_login'
        self.actor_password = 'actor_test_password'
        self.actor_env_name = 'actor_test_env'

    def login_actor(self):
        req = {'environment_name': self.actor_env_name,
            'login': self.actor_login, 'password': self.actor_password}
        return self.login(**req)
