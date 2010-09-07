import logging

from helixcore import mapping
from helixcore.server.wsgi_application import Application

from helixauth.conf.db import transaction
from helixauth.db.dataobject import ActionLog
from helixauth.db.filters import EnvironmentFilter
from helixauth.error import EnvironmentNotFound


class HelixauthApplication(Application):
    def __init__(self, h, p, l):
        self.unauthorized_trackable = ['add_environment']
        tracking_api_calls = ('add_environment',)
        super(HelixauthApplication, self).__init__(h, p, l, tracking_api_calls)

    @transaction()
    def track_api_call(self, remote_addr, s_req, s_resp, authorized_data, curs=None): #IGNORE:W0221
        super(HelixauthApplication, self).track_api_call(remote_addr, s_req, s_resp, authorized_data)

        action_name = authorized_data['action']
        environment_id = None
        try:
            environment_id = self._get_environment_id(curs, authorized_data)
        except EnvironmentNotFound:
            self.logger.log(logging.ERROR, 'Unable to track action for not existed '
                'environment. Request: %s. Response: %s', (s_req, s_resp))

        actor_user_id = None
        user_ids = []

        data = {
            'environment_id': environment_id,
            'custom_actor_user_info': authorized_data.get('custom_actor_user_info'),
            'actor_user_id': actor_user_id,
            'subject_user_ids': user_ids,
            'action': action_name,
            'remote_addr': remote_addr,
            'request': s_req,
            'response': s_resp,
        }
        mapping.insert(curs, ActionLog(**data))


    def _get_environment_id(self, curs, authorized_data):
        action_name = authorized_data['action']
        if action_name in self.unauthorized_trackable:
            if action_name == 'add_environment':
                f = EnvironmentFilter(authorized_data, {}, {})
                environment = f.filter_one_obj(curs)
                return environment.id
