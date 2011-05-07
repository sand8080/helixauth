def apply(curs):
    print 'Creating table action_log'
    curs.execute(
    '''
        CREATE TABLE action_log (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            session_id text,
            custom_actor_info varchar,
            actor_user_id integer,
            FOREIGN KEY (actor_user_id) REFERENCES user_data(id),
            subject_users_ids integer[],
            action varchar NOT NULL,
            request_date timestamp with time zone NOT NULL DEFAULT now(),
            remote_addr text NOT NULL,
            request text NOT NULL,
            response text NOT NULL
        )
    ''')

    print 'Creating index action_log_environment_id_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_environment_id_idx ON action_log(environment_id);
    ''')

    print 'Creating index action_log_environment_id_actor_user_id_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_environment_id_actor_user_id_idx ON action_log(environment_id, actor_user_id);
    ''')

    print 'Creating index action_log_environment_id_session_id_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_environment_id_session_id_idx ON action_log(environment_id, session_id);
    ''')

    print 'Creating index action_log_environment_id_action_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_environment_id_action_idx ON action_log(environment_id, action);
    ''')

    print 'Creating index action_log_environment_id_subject_users_ids_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_environment_id_subject_users_ids_idx ON action_log(environment_id, subject_users_ids);
    ''')


def revert(curs):
    print 'Dropping index action_log_environment_id_subject_users_ids_idx on action_log'
    curs.execute('DROP INDEX IF EXISTS action_log_environment_id_subject_users_ids_idx')

    print 'Dropping index action_log_environment_id_action_idx on action_log'
    curs.execute('DROP INDEX IF EXISTS action_log_environment_id_action_idx')

    print 'Dropping index action_log_environment_id_session_id_idx on action_log'
    curs.execute('DROP INDEX IF EXISTS action_log_environment_id_session_id_idx')

    print 'Dropping index action_log_environment_id_actor_user_id_idx on action_log'
    curs.execute('DROP INDEX IF EXISTS action_log_environment_id_actor_user_id_idx')

    print 'Dropping index action_log_environment_id_idx on action_log'
    curs.execute('DROP INDEX IF EXISTS action_log_environment_id_idx')

    print 'Dropping table action_log'
    curs.execute('DROP TABLE IF EXISTS action_log')
