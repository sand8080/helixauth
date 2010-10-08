def apply(curs):
    print 'Creating table service'
    curs.execute(
    '''
        CREATE TABLE service (
            id serial,
            environment_id integer NOT NULL,
            FOREIGN KEY (environment_id) REFERENCES environment(id),
            name varchar NOT NULL,
            properties varchar[],
            is_active boolean NOT NULL DEFAULT True,
            is_possible_deactiate boolean NOT NULL DEFAULT True
        )
    ''')

    print 'Creating index service_environment_id_name_idx on service'
    curs.execute(
    '''
        CREATE UNIQUE INDEX service_environment_id_name_idx ON service(environment_id, name);
    ''')


def revert(curs):
    print 'Dropping index service_environment_id_name_idx on service'
    curs.execute('DROP INDEX IF EXISTS service_environment_id_name_idx')

    print 'Dropping table service'
    curs.execute('DROP TABLE IF EXISTS service')
