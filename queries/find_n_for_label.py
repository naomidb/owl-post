from thing import Thing

def get_params(connection):
    thing = Thing (connection)
    params = {'Thing': thing,}
    return params

def run(connection, **params):
    thing = params['Thing']

    if thing.category == 'academic_article':
        identity = 'http://purl.org/ontology/bibo/AcademicArticle'
    if thing.category == 'journal':
        identity = 'http://purl.org/ontology/bibo/Journal'
    if thing.category == 'person':
        identity = 'http://xmlns.com/foaf/0.1/Person'

    q = """SELECT ?uri ?label WHERE {{?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{}> . ?uri <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER (regex (?label, "{}")) }}""".format(identity, thing.name)

    response = connection.run_query(q)

    lookup = response.json()
    matches = {}
    for listing in lookup['results']['bindings']:
        name = listing['label']['value']
        url = listing['uri']['value']
        url_n = url.rsplit('/', 1)[-1]
        matches[url_n] = name

    return matches