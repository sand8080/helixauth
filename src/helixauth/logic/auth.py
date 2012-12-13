from uuid import uuid4
import json
import pytz
from datetime import datetime, timedelta
from hashlib import sha512
from random import randint

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.db.dataobject import Session, User
from helixauth.db.filters import SessionFilter, ServiceFilter, GroupFilter
from helixauth.error import SessionExpired, UserAccessDenied, SessionIpChanged
from helixauth.wsgi.protocol import protocol


class Authenticator(object):
    def encrypt_password(self, password, salt):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        h = sha512()
        h.update(password)
        p = h.hexdigest()
        h_s = sha512()
        h_s.update('%s%s' % (p, salt))
        return h_s.hexdigest()

    def salt(self, size=16):
        symbols = ' !@#$%^&*()_+=-,.<>/?0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        res = map(lambda x: symbols[randint(0, len(symbols) - 1)], range(size))
        return ''.join(res)

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

    def create_session(self, curs, env, user, req_info, bind_to_ip=False):
        d = datetime.now(pytz.utc)
        session_data = self._get_session_data(curs, env, user)
        session_data['ip'] = req_info.remote_addr
        session_data['bind_to_ip'] = bind_to_ip
        data = {
            'session_id': '%s' % uuid4(),
            'environment_id': env.id,
            'user_id': user.id,
            'serialized_data': json.dumps(session_data),
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
        f = ServiceFilter(env.id, {'is_active': True}, {}, None)
        srvs = f.filter_objs(curs)
        srvs_id_type_idx = dict([(str(s.id), s.type) for s in srvs])
        return {'services_id_type_idx': srvs_id_type_idx,
            'rights': self._get_user_rights(curs, env, user, srvs)}

    def _get_user_rights(self, curs, env, user, srvs):
        rights = {}
        if user.role != User.ROLE_SUPER:
            f = GroupFilter(env.id, {'ids': user.groups_ids, 'is_active': True},
                {}, None)
            groups = f.filter_objs(curs)
            for g in groups:
                rights_lst = json.loads(g.serialized_rights)
                for r in rights_lst:
                    # String key id for json.encode
                    srv_id = str(r['service_id'])
                    srv_props = r['properties']
                    cur_props = rights.get(srv_id, [])
                    rights[srv_id] = list(set(cur_props + srv_props))
        res = {}
        for srv in srvs:
            if user.role == User.ROLE_SUPER:
                r = json.loads(srv.serialized_properties)
            else:
                r = rights.get(str(srv.id), []) # String key id for json.encode
            res[srv.type] = r
        return res

    def _get_services_id_type_idx(self, curs, env):
        f = ServiceFilter(env.id, {}, {}, None)
        srvs = f.filter_objs(curs)
        idx = dict([(s.id, s.type) for s in srvs])
        return idx

    def check_access(self, session, service_type, prop, req_info):
        sess_data = json.loads(session.serialized_data)
        if sess_data.get('bind_to_ip') and sess_data.get('ip') != req_info.remote_addr:
            raise SessionIpChanged()
        if not self.has_access(sess_data, service_type, prop, req_info):
            raise UserAccessDenied(service_type, prop)

    def has_access(self, sess_data, service_type, prop, req_info):
        rights = sess_data['rights']
        if service_type in rights:
            return prop in rights[service_type]
        else:
            return False
