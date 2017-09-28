def get_params(connection):
    params = {}
    return params

def run(connection, **params):
    q = """ select ?label ?u where { ?u <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> . ?u <http://www.w3.org/2000/01/rdf-schema#label> ?label . } """

    print('=' * 20 + '\nGenerating author list\n' + '=' * 20)
    response = connection.run_query(q)

    author_dump = response.json()
    all_authors = {}
    for listing in author_dump['results']['bindings']:
        a_name = listing['label']['value']
        a_url = listing['u']['value']
        a_n = a_url.rsplit('/', 1)[-1]
        all_authors[a_name] = a_n

    return all_authors