from uuid import uuid4
import cjson
import pytz
from datetime import datetime, timedelta

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.dataobject import Session, User
from helixauth.db.filters import SessionFilter, EnvironmentFilter, UserFilter
from helixauth.error import UserAuthError


class Authentifier(object):
    def get_credentials(self, data):
        '''
        returns (session, environment, user)
        '''
        session = self._get_session(data)
        env, user = self._extract_credentials(session)
        return (session, env, user)

    def _get_session(self, data):
        session_id = data['session_id']
        return self._update_session(session_id)

    @transaction()
    def _update_session(self, session_id, curs=None):
        valid_date = self._session_valid_update_date()
        f = SessionFilter({'session_id': session_id,
            'to_update_date': valid_date}, {}, {})
        session = f.filter_one_obj(curs, for_update=True)
        session.update_date = datetime.now(pytz.utc)
        mapping.save(curs, session)
        return session

    @transaction()
    def _extract_credentials(self, session, curs=None):
        '''
        returns (env, user)
        '''
        f = EnvironmentFilter({'environment_id': session.environment_id},
            {}, {})
        env = f.filter_one_obj(curs)

        f = UserFilter(env, {'id': session.user_id}, {}, {})
        user = f.filter_one_obj(curs)

        return env, user

    def _session_valid_update_date(self):
        cur_date = datetime.now(pytz.utc)
        valid_period = timedelta(minutes=settings.session_valid_minutes)
        return cur_date - valid_period

    def create_session(self, curs, env, user):
        d = datetime.now(pytz.utc)
        rights = self._get_access_rights(env, user)
        sz_data = cjson.encode({'rights': rights})

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

    def _get_access_rights(self, env, user):
        if user.role == User.ROLE_SUPER:
            return {}
        else:
            raise NotImplemented

    def check_access(self, session, user, action):
        if user.role == User.ROLE_SUPER:
            return True
        else:
            data = cjson.decode(session.sz_data)
            rights = data['rights']
            return action in rights and rights[action] is True
        raise UserAuthError("User %s access denied to action %s" %
            (user.login, action))

