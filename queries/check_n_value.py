from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'N number': thing,}
    return params

def run(connection, **params):
    for key, val in params.items():
        print('=' * 20 + "\nRunning n check\n" + '=' * 20)
        thing = val
    uri = connection.vivo_url + thing.n_num
    q = """SELECT ?u WHERE{{?u <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Thing> . FILTER (?u=<{}>)}}""".format(uri)

    response = connection.run_query(q)

    n_check = response.json()
    try: 
        if n_check['results']['bindings'][0]['u']:
            return True
    except IndexError as e:
        if e.message != "list index out of range":
            raise
        else:
            return False
