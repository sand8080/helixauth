def apply(curs):
    print 'Creating table session'
    curs.execute(
    '''
        CREATE TABLE session (
            id serial,
            session_id varchar NOT NULL,
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            user_id integer NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user_data(id),
            serialized_data varchar NOT NULL,
            PRIMARY KEY(id),
            start_date timestamp with time zone NOT NULL,
            update_date timestamp with time zone NOT NULL
        )
    ''')

    print 'Creating index session_session_id_idx on session'
    curs.execute(
    '''
        CREATE INDEX session_session_id_idx ON session(session_id);
    ''')

    print 'Creating index session_session_id_update_date_idx on session'
    curs.execute(
    '''
        CREATE INDEX session_session_id_update_date_idx ON session(session_id, update_date);
    ''')


def revert(curs):
    print 'Dropping index session_session_id_update_date_idx on session'
    curs.execute('DROP INDEX IF EXISTS session_user_id_idx')

    print 'Dropping index session_session_id_idx on session'
    curs.execute('DROP INDEX IF EXISTS session_user_id_idx')

    print 'Dropping table session'
    curs.execute('DROP TABLE IF EXISTS session')
