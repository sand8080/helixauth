import unittest

from helixauth.test.wsgi.test_protocol import ProtocolTestCase #IGNORE:W0611 @UnusedImport

from helixauth.test.logic.test_login import LoginTestCase #IGNORE:W0611 @UnusedImport
from helixauth.test.logic.test_environment import EnvironmentTestCase #IGNORE:W0611 @UnusedImport
from helixauth.test.logic.test_user import UserTestCase #IGNORE:W0611 @UnusedImport
from helixauth.test.logic.test_service import ServiceTestCase #IGNORE:W0611 @UnusedImport
from helixauth.test.logic.test_group import GroupTestCase #IGNORE:W0611 @UnusedImport
from helixauth.test.logic.test_access import AccessTestCase #IGNORE:W0611 @UnusedImport

from helixauth.test.logic.test_action_log import ActionLogTestCase #IGNORE:W0611 @UnusedImport


if __name__ == '__main__':
    unittest.main()
