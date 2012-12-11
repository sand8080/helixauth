import unittest

from helixauth.test.logic.actor_logic_test import ActorLogicTestCase
from helixcore.error import RequestProcessingError
from helixauth.db.filters import GroupFilter
from helixauth.conf.db import transaction


class GroupTestCase(ActorLogicTestCase):
    def setUp(self):
        super(GroupTestCase, self).setUp()
        self.create_actor_env()

    def test_add_group(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        # Checking group (environment_id, name) is unique
        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 2, 'properties':['b']}]}
        self.assertRaises(RequestProcessingError, self.add_group, **req)

        req = {'name': 'env_1', 'su_email': 'l@h.com', 'su_password': 'p'}
        resp = self.add_environment(**req)
        self.check_response_ok(resp)

        # Checking name duplication is possible in different environments
        sess_id = resp['session_id']
        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 2, 'properties':['b']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

    def test_modify_group(self):
        sess_id = self.login_actor()
        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'new_name': 'grp1', 'id': 1,
            'new_rights': [{'service_id': 1, 'properties':['a', 'b']}]}
        resp = self.modify_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'name': 'grp2',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'id': 1, 'new_name': 'grp2'}
        self.assertRaises(RequestProcessingError, self.modify_group, **req)

    def _groups_num(self, sess_id):
        req = {'session_id': sess_id, 'filter_params': {}, 'paging_params': {}}
        resp = self.get_groups(**req)
        self.check_response_ok(resp)
        return len(resp['groups'])

    @transaction()
    def test_delete_group(self, curs=None):
        sess_id = self.login_actor()
        groups_num = self._groups_num(sess_id)

        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'name': 'grp1',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        session = self.get_session(sess_id)
        f = GroupFilter(session.environment_id, {}, {}, None)
        self.assertEquals(groups_num + 2, f.filter_objs_count(curs))

        req = {'session_id': sess_id, 'id': 1}
        resp = self.delete_group(**req)
        self.check_response_ok(resp)
        self.assertEquals(groups_num + 1, f.filter_objs_count(curs))

    def test_get_groups(self, curs=None):
        sess_id = self.login_actor()
        groups_num = self._groups_num(sess_id)

        req = {'session_id': sess_id, 'name': 'grp0',
            'rights': [{'service_id': 1, 'properties':['a']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'name': 'grp1',
            'rights': [{'service_id': 1, 'properties':['a', 'c']}]}
        resp = self.add_group(**req)
        self.check_response_ok(resp)

        req = {'session_id': sess_id, 'filter_params': {},
            'paging_params': {}}
        resp = self.get_groups(**req)
        self.check_response_ok(resp)
        self.assertEquals(groups_num + 2, len(resp['groups']))


if __name__ == '__main__':
    unittest.main()