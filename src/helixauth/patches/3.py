def apply(curs):
    print 'Creating table environment'
    curs.execute(
    '''
        CREATE TABLE environment (
            id serial,
            name varchar NOT NULL,
            PRIMARY KEY(id),
            UNIQUE(name)
        )
    ''')


def revert(curs):
    print 'Dropping table environment'
    curs.execute('DROP TABLE environment')
