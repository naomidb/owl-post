from thing import Thing

def get_params(connection):
    thing = Thing (connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    thing = params['Thing']

    q = """SELECT ?uri ?issn WHERE {{?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/Journal> . ?uri <http://purl.org/ontology/bibo/doi> ?issn . FILTER (regex (?issn, "{}")) }}""".format(thing.name)

    print('=' * 20 + "\nFinding n number\n" + '=' * 20)
    response = connection.run_query(q)

    lookup = response.json()
    matches = {}
    for listing in lookup['results']['bindings']:
        issn = listing['issn']['value']
        url = listing['uri']['value']
        url_n = url.rsplit('/', 1)[-1]
        matches[url_n] = issn

    return matches