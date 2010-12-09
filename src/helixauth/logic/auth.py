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
from helixauth.wsgi.protocol import protocol


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

    def get_auth_api_actions(self):
        marker = '_request'
        actions = [c.name for c in protocol if c.name.endswith(marker)]
        actions = map(lambda x: x.replace(marker, ''), actions)
        return actions

    def _get_session_data(self, curs, env, user):
        f = ServiceFilter(env.id, {}, {}, None)
        srvs = f.filter_objs(curs)
        srvs_id_type_idx = dict([(str(s.id), s.type) for s in srvs])
        return {'services_id_type_idx': srvs_id_type_idx,
            'rights': self._get_user_rights(curs, env, user, srvs)}

    def _get_user_rights(self, curs, env, user, srvs):
        rights = {}
        if user.role != User.ROLE_SUPER:
            f = UserRightsFilter(env.id, {'user_id': user.id}, {}, None)
            u_r = f.filter_one_obj(curs)
            if u_r:
                rights_l = cjson.decode(u_r.serialized_rights)
                # String key id for json.encode
                rights = dict([(str(el['service_id']), el['properties']) for el in rights_l])
            else:
                rights = {}

        res = {}
        for srv in srvs:
            if user.role == User.ROLE_SUPER:
                r = srv.properties
            else:
                r = rights.get(str(srv.id), []) # String key id for json.encode
            res[srv.type] = r
        return res

    def _get_services_id_type_idx(self, curs, env):
        f = ServiceFilter(env.id, {}, {}, None)
        srvs = f.filter_objs(curs)
        # cjson can't encode dicts with non string keys
        idx = dict([(str(s.id), s.type) for s in srvs])
        return idx

    def check_access(self, session, service_type, property):
        if not self.has_access(session, service_type, property):
            raise UserAccessDenied(property)

    def has_access(self, session, service_type, property):
        data = cjson.decode(session.serialized_data)
        rights = data['rights']
        if service_type in rights:
            return property in rights[service_type]
        else:
            return False
