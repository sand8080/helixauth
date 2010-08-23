def apply(curs):
    print 'Creating table action_log'
    curs.execute(
    '''
        CREATE TABLE action_log (
            id serial,
            PRIMARY KEY(id),
            user_id integer,
            FOREIGN KEY (user_id) REFERENCES user(id),
            custom_user_info varchar,
            action varchar NOT NULL,
            request_date timestamp with time zone NOT NULL DEFAULT now(),
            remote_addr text NOT NULL,
            request text NOT NULL,
            response text NOT NULL
        )
    ''')

    print 'Creating index action_log_user_id_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_user_id_idx ON action_log(user_id);
    ''')

    print 'Creating index action_log_user_id_action_idx on action_log'
    curs.execute(
    '''
        CREATE INDEX action_log_user_id_action_idx ON action_log(user_id, action);
    ''')


def revert(curs):
    print 'Dropping index action_log_user_id_action_idx on action_log'
    curs.execute('DROP INDEX action_log_user_id_action_idx')

    print 'Dropping index action_log_user_id_idx on action_log'
    curs.execute('DROP INDEX action_log_user_id_idx')

    print 'Dropping table action_log'
    curs.execute('DROP TABLE action_log')
