from helixcore.install import install

# setting test environment variables
import helixauth.test.test_environment #IGNORE:W0611 @UnusedImport

from helixauth.conf.db import get_connection, put_connection
from helixauth.conf.settings import patch_table_name
from helixauth.test.root_test import RootTestCase
from helixauth.test.test_environment import patches_path


class DbBasedTestCase(RootTestCase):
    def setUp(self):
        install.execute('reinit', get_connection, put_connection, patch_table_name, patches_path)
