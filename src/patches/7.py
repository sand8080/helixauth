def apply(curs):
    print 'Creating table group'
    curs.execute(
    '''
        CREATE TABLE group_data (
            id serial,
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            name varchar NOT NULL,
            is_active boolean NOT NULL DEFAULT True,
            serialized_rights varchar NOT NULL,
            is_default boolean NOT NULL DEFAULT False,
            UNIQUE(environment_id, name)
        )
    ''')

    print 'Creating index group_data_environment_id_idx on group_data'
    curs.execute(
    '''
        CREATE INDEX group_environment_id_idx ON group_data(environment_id);
    ''')

    print 'Creating unique index group_data_environment_id_name_idx on group_data'
    curs.execute(
    '''
        CREATE UNIQUE INDEX group_environment_id_name_idx ON group_data(environment_id, name);
    ''')


def revert(curs):
    print 'Dropping unique index group_data_environment_id_name_idx on group_data'
    curs.execute('DROP INDEX IF EXISTS group_data_environment_id_name_idx')

    print 'Dropping index group_data_environment_id_idx on group_data'
    curs.execute('DROP INDEX IF EXISTS group_data_environment_id_idx')

    print 'Dropping table group'
    curs.execute('DROP TABLE IF EXISTS group_data')
