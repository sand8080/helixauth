def apply(curs):
    print 'Creating table user_data'
    curs.execute(
    '''
        CREATE TABLE user_data (
            id serial,
            environment_id integer,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            login varchar NOT NULL,
            password varchar NOT NULL,
            PRIMARY KEY(id),
            UNIQUE(login)
        )
    ''')

    print 'Creating index user_data_login_password_idx on user_data'
    curs.execute(
    '''
        CREATE INDEX user_data_login_password_idx ON user_data(login, password);
    ''')

    print 'Creating index user_data_environment_id_login_password_idx on user_data'
    curs.execute(
    '''
        CREATE INDEX user_data_environment_id_login_password_idx ON user_data(environment_id, login, password);
    ''')


def revert(curs):
    print 'Dropping index user_data_environment_id_login_password_idx on user_data'
    curs.execute('DROP INDEX IF EXISTS user_data_environment_id_login_password_idx')

    print 'Dropping index user_data_login_password_idx on user_data'
    curs.execute('DROP INDEX IF EXISTS user_data_login_password_idx')

    print 'Dropping table user_data'
    curs.execute('DROP TABLE IF EXISTS user_data')
