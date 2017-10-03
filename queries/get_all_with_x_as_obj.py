from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'N number': thing,}
    return params

def run(connection, **params):
    obj = params['Upload_url'] + params['N number'].n_num

    q = """ SELECT ?s ?p ?o WHERE{{?s ?p <{}> .}} """.format(obj)

    print('=' * 20 + '\nGenerating\n' + '=' * 20)
    response = connection.run_query(q)
    print(response)

    #Navigate json
    triple_dump = response.json()
    triples = []
    for listing in triple_dump['results']['bindings']:
        subj = listing['s']['value']
        pred = listing['p']['value']
        trip = "<" + subj + "> <" + pred + "> <" + obj + ">"
        triples.append(trip)

    return triples