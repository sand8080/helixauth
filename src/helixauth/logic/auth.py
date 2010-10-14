from uuid import uuid4
import cjson
import pytz
from datetime import datetime, timedelta
from hashlib import sha256

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.dataobject import Session, User
from helixauth.db.filters import SessionFilter, ServiceFilter, UserRightsFilter
from helixauth.error import SessionExpired, UserAccessDenied


class Authentifier(object):
    def encrypt_password(self, password):
        h = sha256()
        h.update(password)
        return h.hexdigest()

    @transaction()
    def get_session(self, session_id, curs=None):
        f = SessionFilter({'session_id': session_id}, {}, {})
        session = f.filter_one_obj(curs, for_update=True)

        valid_date = self._session_expiration_date()
        if session.update_date > valid_date:
            session.update_date = datetime.now(pytz.utc)
            mapping.save(curs, session)
        else:
            raise SessionExpired()
        return session

    def _session_expiration_date(self):
        cur_date = datetime.now(pytz.utc)
        valid_period = timedelta(minutes=settings.session_valid_minutes)
        return cur_date - valid_period

    def create_session(self, curs, env, user):
        d = datetime.now(pytz.utc)
        session_data = self._get_session_data(curs, env, user)
        data = {
            'session_id': '%s' % uuid4(),
            'environment_id': env.id,
            'user_id': user.id,
            'serialized_data': cjson.encode(session_data),
            'start_date': d,
            'update_date': d,
        }
        session = Session(**data)
        mapping.save(curs, session)
        return session

    def _get_session_data(self, curs, env, user):
        if user.role == User.ROLE_SUPER:
            return {}
        else:
            d = {}
            d['services_name_id_idx'] = self._get_services_name_id_idx(curs, env)
            d['rights'] = self._get_user_rights(curs, env, user)
            return d

    def _get_user_rights(self, curs, env, user):
        f = UserRightsFilter(env.id, {'user_id': user.id}, {}, None)
        user_rights = f.filter_one_obj(curs)
        if user_rights:
            rights_l = cjson.decode(user_rights.serialized_rights)
            # cjson can't encode dicts with non string keys
            rights = dict([(str(el['service_id']), el['properties']) for el in rights_l])
            return rights
        else:
            return {}

    def _get_services_name_id_idx(self, curs, env):
        f = ServiceFilter(env.id, {}, {}, None)
        srvs = f.filter_objs(curs)
        # cjson can't encode dicts with non string keys
        srvs_name_id_idx = dict([(s.name, str(s.id)) for s in srvs])
        return srvs_name_id_idx

    def check_access(self, session, user, property):
        if user.role != User.ROLE_SUPER:
            data = cjson.decode(session.serialized_data)
            rights = data['rights']
            int_srvs_ids = map(int, rights.keys())
            auth_srv_id = str(min(int_srvs_ids))
            print 'property ', auth_srv_id, property, rights
            if property not in rights[auth_srv_id]:
                raise UserAccessDenied(user.login, property)
