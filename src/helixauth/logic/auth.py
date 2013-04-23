from uuid import uuid4
import json
import pytz
from datetime import datetime, timedelta
from hashlib import sha512
from random import randint
import memcache

from helixcore import mapping

from helixauth.conf import settings
from helixauth.conf.db import transaction
from helixauth.conf.log import logger
from helixauth.db.dataobject import Session, User, Service
from helixauth.db.filters import SessionFilter, ServiceFilter, GroupFilter
from helixauth.error import SessionExpired, UserAccessDenied, SessionIpChanged,\
    SessionTooLargeFixedLifetime
from helixauth.wsgi.protocol import protocol


class Authenticator(object):
    def __init__(self):
        self.mem_cache = memcache.Client([settings.session_memcached_addr])

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
    def _get_session_db(self, session_id, curs=None):
        f = SessionFilter({'session_id': session_id}, {}, {})
        session = f.filter_one_obj(curs, for_update=True)
        valid_after_date = self._session_valid_after_update_date()
        if session.update_date > valid_after_date:
            self._set_update_date(session)
            mapping.save(curs, session)
        else:
            raise SessionExpired()
        return session

    def _save_session_to_cache(self, session):
        str_sess_id = session.session_id.encode('utf8')
        expire_sec = settings.session_valid_minutes * 60
        expire_dt = session.update_date + timedelta(seconds=expire_sec)
        curr_dt = datetime.now(pytz.utc)
        if expire_dt <= curr_dt:
            logger.debug("Session %s expired. Not saving to cache", session.session_id)
        else:
            expire_delta = expire_dt - curr_dt
            # Workaround for excluding creation non expiring sessions
            cache_expire_sec = expire_delta.seconds if expire_delta.seconds else 1
            logger.debug("Saving session %s to cache. Current date: %s. " \
                "Session update date: %s. " \
                "Session in cache expired after %s seconds",
                session.session_id, curr_dt, session.update_date, expire_delta.seconds)
            self.mem_cache.set(str_sess_id, session,
                time=cache_expire_sec)

    def _set_update_date(self, session):
        sess_data = json.loads(session.serialized_data)
        if not sess_data.get('fixed_lifetime'):
            logger.debug("Updating session update date")
            session.update_date = datetime.now(pytz.utc)
        else:
            logger.debug("Not updating update date of " \
                "session with fixed lifetime")

    def _get_cached_session(self, session_id):
        logger.debug("Getting session from memcached")
        str_sess_id = session_id.encode('utf8')
        session = None
        try:
            session = self.mem_cache.get(str_sess_id)
        except Exception, e:
            logger.info("Session %s not found in memcached: %s",
                str_sess_id, e)
        if session is None or session.update_date <= self._session_valid_after_update_date():
            logger.debug("Valid session %s not found in memcached", str_sess_id)
            session = self._get_session_db(session_id)
            logger.debug("Session %s added into memcached", str_sess_id)
        else:
            logger.debug("Session %s got from memcached", str_sess_id)
            self._set_update_date(session)
        self._save_session_to_cache(session)
        return session

    def get_session(self, session_id):
        """
        gets session and updates update_date
        """
        if settings.session_caching_enabled:
            session = self._get_cached_session(session_id)
        else:
            session = self._get_session(session_id)
        return session

    def _session_valid_after_update_date(self):
        cur_date = datetime.now(pytz.utc)
        valid_period = timedelta(minutes=settings.session_valid_minutes)
        return cur_date - valid_period

    def create_session(self, curs, env, user, req_info,
        bind_to_ip=False, lifetime_minutes=None):
        return self.__create_session(curs, env, user,
            req_info, bind_to_ip=bind_to_ip,
            lifetime_minutes=lifetime_minutes)

    def create_restore_password_session(self, curs, env, user, req_info,
        bind_to_ip=False, lifetime_minutes=None):
        services_access_list = {Service.TYPE_AUTH: ['set_password_self']}
        return self.__create_session(curs, env, user,
            req_info, bind_to_ip=bind_to_ip,
            lifetime_minutes=lifetime_minutes,
            services_access_list=services_access_list)

    def __merge_access_list(self, session_data, services_access_list):
        if services_access_list is not None:
            r_src = session_data.get('rights', {})
            r_res = {}
            for srv, props_acl in services_access_list.items():
                if srv in r_src:
                    props_src = r_src.get(srv, [])
                    props_res = filter(lambda x: x in props_src, props_acl)
                    r_res[srv] = props_res
            session_data['rights'] = r_res
        return session_data

    def __create_session(self, curs, env, user, req_info,
        bind_to_ip=False, lifetime_minutes=None,
        services_access_list=None):
        """
        @param curs - db cursor
        @param env - environment dataobject
        @param user - user dataobject
        @param req_info - request info, for fetching ip address
        @param bind_to_ip - if True session will be binded with ip from req_info.
          Usage session binded to ip from another ip generates AccessDenied error.
        @param lifetime_minutes - session lifetime. If not None session will be
          valid number of specified minutes after session generating time.
        @param services_acess_list - dict of specified acl for generating sessions
          with restricted access. Access list can't add privileges to user - it used
          only for restriction. All superior privileges will be ignored.
          This behaviour used in password restoration.
        """
        d = datetime.now(pytz.utc)
        session_data = self._get_session_data(curs, env, user)
        self.__merge_access_list(session_data, services_access_list)
        session_data['ip'] = req_info.remote_addr
        session_data['bind_to_ip'] = bind_to_ip
        session_data['fixed_lifetime'] = lifetime_minutes is not None
        if lifetime_minutes is not None:
            if lifetime_minutes > settings.session_max_fixed_lifetime_minutes:
                raise SessionTooLargeFixedLifetime()
            session_data['fixed_lifetime'] = True
            td = lifetime_minutes - settings.session_valid_minutes
            upd_d = d + timedelta(minutes=td)
        else:
            session_data['fixed_lifetime'] = False
            upd_d = d
        data = {
            'session_id': '%s' % uuid4(),
            'environment_id': env.id,
            'user_id': user.id,
            'serialized_data': json.dumps(session_data),
            'start_date': d,
            'update_date': upd_d,
        }
        session = Session(**data)
        mapping.save(curs, session)

        # adding session into memcached
        if settings.session_caching_enabled:
            self._save_session_to_cache(session)

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
        return {'services_id_type_idx': srvs_id_type_idx, 'lang': user.lang,
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
