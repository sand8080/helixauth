from helixcore import mapping
from helixcore.server.wsgi_application import Application

from helixauth.conf.db import transaction
from helixauth.db.dataobject import ActionLog


class HelixauthApplication(Application):
    def __init__(self, h, p, l):
        self.unauthorized_trackable = ['add_environment']
        tracking_api_calls = ('add_environment', 'login')
        super(HelixauthApplication, self).__init__(h, p, l, tracking_api_calls)

    @transaction()
    def track_api_call(self, remote_addr, s_req, s_resp,
        action_name, processed_data, curs=None): #IGNORE:W0221
        super(HelixauthApplication, self).track_api_call(remote_addr, s_req, s_resp,
            action_name, processed_data)


        actor_user_id = processed_data.get('actor_user_id')
        custom_actor_info = processed_data.get('custom_actor_user_info')
        environment_id = processed_data.get('environment_id')
        user_ids = []

        data = {
            'environment_id': environment_id,
            'custom_actor_user_info': custom_actor_info,
            'actor_user_id': actor_user_id,
            'subject_user_ids': user_ids,
            'action': action_name,
            'remote_addr': remote_addr,
            'request': s_req,
            'response': s_resp,
        }
        mapping.insert(curs, ActionLog(**data))
