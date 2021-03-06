def apply(curs):
    print 'Creating table service'
    curs.execute(
    '''
        CREATE TABLE service (
            id serial,
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            name varchar NOT NULL,
            type varchar NOT NULL,
            serialized_properties varchar,
            is_active boolean NOT NULL DEFAULT True,
            is_possible_deactiate boolean NOT NULL DEFAULT True
        )
    ''')

    print 'Creating index service_environment_id_type_idx on service'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_environment_id_type_idx ON service(environment_id, type);
    ''')


def revert(curs):
    print 'Dropping index service_environment_id_type_idx on service'
    curs.execute('DROP INDEX IF EXISTS service_environment_id_type_idx')

    print 'Dropping table service'
    curs.execute('DROP TABLE IF EXISTS service')
