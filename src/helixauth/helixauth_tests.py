import unittest

from helixauth.test.logic.test_environment import EnvironmentTestCase #IGNORE:W0611 @UnusedImport
from helixauth.test.validator.test_validator import ValidatorTestCase #IGNORE:W0611 @UnusedImport

from helixauth.test.wsgi.test_application_loading import ApplicationTestCase #IGNORE:W0611 @UnusedImport


if __name__ == '__main__':
    unittest.main()
