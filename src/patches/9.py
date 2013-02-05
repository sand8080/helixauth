def apply(curs):
    print 'Creating table notification'
    curs.execute(
    '''
        CREATE TABLE notification (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            event varchar NOT NULL,
            is_active boolean NOT NULL DEFAULT True,
            serialized_messages varchar
        )
    ''')

    print 'Creating notification_environment_id_idx on notification'
    curs.execute(
    '''
        CREATE INDEX notification_environment_id_idx ON notification(environment_id);
    ''')

    print 'Creating unique index notification_environment_id_event_idx on notification'
    curs.execute(
    '''
        CREATE UNIQUE INDEX notification_environment_id_event_idx ON notification(environment_id, event);
    ''')


def revert(curs):
    print 'Dropping unique index notification_environment_id_event_idx on notification'
    curs.execute('DROP INDEX IF EXISTS notification_environment_id_event_idx')

    print 'Dropping index notification_environment_id_idx on notification'
    curs.execute('DROP INDEX IF EXISTS notification_environment_id_idx')

    print 'Dropping table notification'
    curs.execute('DROP TABLE IF EXISTS notification')
