from journal import Journal

def get_params(connection):
    journal = Journal(connection)
    params = {'Journal': journal}
    return params

def run(connection, **params):
    journal = params.get('Journal')
    upload_url = connection.vivo_url
    print(journal, type(journal))

    if journal.n_num == None:
        journal.create_n()

    q = """
    INSERT DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
        {{
            <{url}{Journal.n_num}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/Journal> .
            <{url}{Journal.n_num}> <http://www.w3.org/2000/01/rdf-schema#label> "{Journal.title}" .
        }}
    }}
    """.format(url=upload_url ,Journal=journal)

    print('=' * 20 + "\nCreating new journal\n" + '=' * 20)
    response = connection.run_update(q)
    return response