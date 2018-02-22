from thing import Thing

def get_params(connection):
    thing = Thing (connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    thing = params['Thing']

    q = """SELECT ?uri ?doi WHERE {{?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle> . ?uri <http://purl.org/ontology/bibo/doi> ?doi . FILTER (regex (?doi, "{}")) }}""".format(thing.name)

    print('=' * 20 + "\nFinding n number\n" + '=' * 20)
    response = connection.run_query(q)

    lookup = response.json()
    matches = {}
    for listing in lookup['results']['bindings']:
        doi = listing['doi']['value']
        url = listing['uri']['value']
        url_n = url.rsplit('/', 1)[-1]
        matches[url_n] = doi

    return matches