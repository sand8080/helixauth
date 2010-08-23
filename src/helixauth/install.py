#!/usr/bin/env python

import os
import sys
from helixcore.install.install import execute, COMMANDS
from helixbilling.conf.db import get_connection, put_connection
from helixbilling.conf.settings import patch_table_name

def get_patches_path():
    return os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        'patches'
    )

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print 'usage: %s %s' % (sys.argv[0], '|'.join(COMMANDS))
        sys.exit(1)
    execute(sys.argv[1], get_connection, put_connection, patch_table_name, get_patches_path())

if __name__ == '__main__':
    main()
