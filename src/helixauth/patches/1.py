from helixauth.conf.settings import patch_table_name


def apply(curs):
    print 'Creating table %s' % patch_table_name
    curs.execute('CREATE TABLE %s (id serial, name varchar, path varchar, date timestamp)' % patch_table_name)


def revert(curs):
    print 'Dropping table %s' % patch_table_name
    curs.execute('DROP TABLE %s' % patch_table_name)
