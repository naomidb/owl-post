from journal import Journal

def get_params(connection):
    journal = Journal(connection)
    params = {'New Journal': journal}
    return params

def run(connection, **params):
    journal = params.get('New Journal')
    print(journal, type(journal))

    if journal.n_num == None:
        journal.create_n()

    q = """
    INSERT DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
        {{
            <http://vivo.school.edu/individual/{Journal.n_num}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/Journal> .
            <http://vivo.school.edu/individual/{Journal.n_num}> <http://www.w3.org/2000/01/rdf-schema#label> "{Journal.title}" .
        }}
    }}
    """.format(Journal=journal)

    print('=' * 20 + "\nCreating new journal\n" + '=' * 20)
    response = connection.run_update(q)
    return response