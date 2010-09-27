from uuid import uuid4
import cjson
import pytz
from datetime import datetime, timedelta

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.dataobject import Session, User
from helixauth.db.filters import SessionFilter


class Authentifier(object):
#    @transaction()
#    def get_credentials(self, data, curs=None):
#        '''
#        returns (session, environment, user)
#        '''
#        session = self._get_session(data)
#        environment = self._get_environment_from_sesion(curs, session)
#        user = self._get_user_from_sesion(curs, environment, session)
#        return (session, environment, user)
#
#    def check_access(self, session, user):
#        pass
#
#    def _get_session(self, data):
#        if 'session_id' in data:
#            session_id = data['session_id']
#            return self._update_session(session_id)
#        else:
#            login = data['login']
#            password = data['password']
#            env_name = data['environment_name']
#            # auth user
#            # create session
#            return None
#
#    @transaction()
#    def _update_session(self, session_id, curs=None):
#        f = SessionFilter({'session_id': session_id}, {}, {})
#        session = f.filter_one_obj(curs, for_update=True)
#        session.update_date = datetime.now(pytz.utc)
#        mapping.save(curs, session)
#        return session

    def session_valid_until(self):
        cur_date = datetime.now(pytz.utc)
        valid_period = timedelta(minutes=settings.session_valid_minutes)
        return cur_date + valid_period

    def create_session(self, curs, env, user, sz_data):
        d = datetime.now(pytz.utc)
        data = {
            'session_id': '%s' % uuid4(),
            'environment_id': env.id,
            'user_id': user.id,
            'serialized_data': cjson.encode(sz_data),
            'start_date': d,
            'update_date': d,
        }
        session = Session(**data)
        mapping.save(curs, session)
        return session

    def get_access_rights(self, env, user):
        if user.role == User.ROLE_SUPER:
            return {}
        else:
            raise NotImplemented

    def get_serialized_access_rights(self, env, user):
        return cjson.encode(self.get_access_rights(env, user))

    def is_access_granted(self, user, action, rights):
        if user.role == User.ROLE_SUPER:
            return True
        else:
            return action in rights and rights[action] is True