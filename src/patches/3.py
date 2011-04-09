def apply(curs):
    print 'Creating table user_data'
    curs.execute(
    '''
        CREATE TABLE user_data (
            id serial,
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            login varchar NOT NULL,
            password varchar NOT NULL,
            salt varchar NOT NULL,
            is_active boolean NOT NULL DEFAULT True,
            role varchar NOT NULL CHECK(role in ('super', 'user')),
            groups_ids integer[] DEFAULT ARRAY[]::integer[],
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index user_data_environment_id_idx on user_data'
    curs.execute(
    '''
        CREATE INDEX user_data_environment_id_idx ON user_data(environment_id);
    ''')

    print 'Creating unique index user_data_environment_id_login_idx on user_data'
    curs.execute(
    '''
        CREATE UNIQUE INDEX user_data_environment_id_login_idx ON user_data(environment_id, login);
    ''')


def revert(curs):
    print 'Dropping user_data_environment_id_idx on user_data'
    curs.execute('DROP INDEX IF EXISTS user_data_environment_id_idx')

    print 'Dropping unique index user_data_environment_id_login_idx on user_data'
    curs.execute('DROP INDEX IF EXISTS user_data_environment_id_login_idx')

    print 'Dropping table user_data'
    curs.execute('DROP TABLE IF EXISTS user_data')
