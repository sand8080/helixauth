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
            is_active boolean NOT NULL DEFAULT True,
            role varchar NOT NULL CHECK(role in ('super', 'user')),
            groups_ids integer[] DEFAULT ARRAY[]::integer[],
            PRIMARY KEY(id),
            UNIQUE(environment_id, login)
        )
    ''')

    print 'Creating index user_data_environment_id_idx on user_data'
    curs.execute(
    '''
        CREATE INDEX user_data_environment_id_idx ON user_data(environment_id);
    ''')

    print 'Creating index user_data_environment_id_login_password_idx on user_data'
    curs.execute(
    '''
        CREATE INDEX user_data_environment_id_login_password_idx ON user_data(environment_id, login, password);
    ''')


def revert(curs):
    print 'Dropping user_data_environment_id_idx on user_data'
    curs.execute('DROP INDEX IF EXISTS user_data_environment_id_idx')

    print 'Dropping index user_data_environment_id_login_password_idx on user_data'
    curs.execute('DROP INDEX IF EXISTS user_data_environment_id_login_password_idx')

    print 'Dropping table user_data'
    curs.execute('DROP TABLE IF EXISTS user_data')
