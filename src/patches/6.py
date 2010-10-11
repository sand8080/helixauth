def apply(curs):
    print 'Creating table user_rights'
    curs.execute(
    '''
        CREATE TABLE user_rights (
            id serial,
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            user_id integer NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user_data(id),
            serialized_rights varchar NOT NULL
        )
    ''')

    print 'Creating index user_rights_environment_id_idx on user_rights'
    curs.execute(
    '''
        CREATE INDEX user_rights_environment_id_idx ON user_rights(environment_id);
    ''')

    print 'Creating index user_rights_user_id_idx on user_rights'
    curs.execute(
    '''
        CREATE INDEX user_rights_user_id_idx ON user_rights(user_id);
    ''')


def revert(curs):
    print 'Dropping index user_rights_user_id_idx on user_rights'
    curs.execute('DROP INDEX IF EXISTS user_rights_user_id_idx')

    print 'Dropping index user_rights_environment_id_idx on user_rights'
    curs.execute('DROP INDEX IF EXISTS user_rights_environment_id_idx')

    print 'Dropping table user_rights'
    curs.execute('DROP TABLE IF EXISTS user_rights')
