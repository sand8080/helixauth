def apply(curs):
    print 'Creating table notification'
    curs.execute(
    '''
        CREATE TABLE notification (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            lang varchar NOT NULL CHECK(lang in ('en', 'ru')),
            is_active boolean NOT NULL DEFAULT True,
            name varchar NOT NULL,
            message varchar NOT NULL
        )
    ''')

    print 'Creating notification_environment_id_idx on notification'
    curs.execute(
    '''
        CREATE INDEX notification_environment_id_idx ON notification(environment_id);
    ''')

    print 'Creating unique index notification_environment_id_name_lang_idx on notification'
    curs.execute(
    '''
        CREATE UNIQUE INDEX notification_environment_id_name_lang_idx ON notification(environment_id, name, lang);
    ''')


def revert(curs):
    print 'Dropping unique index notification_environment_id_name_lang_idx on notification'
    curs.execute('DROP INDEX IF EXISTS notification_environment_id_name_lang_idx')

    print 'Dropping index notification_environment_id_idx on notification'
    curs.execute('DROP INDEX IF EXISTS notification_environment_id_idx')

    print 'Dropping table notification'
    curs.execute('DROP TABLE IF EXISTS notification')
