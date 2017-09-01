from thing import Thing

def get_params(connection):
    thing = Thing(connection)
    params = {'N number': thing,}
    return params

def run(connection, **params):
    uri = connection.vivo_url + n_num
    q = """SELECT ?u WHERE{{?u <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Thing> . FILTER (?u=<{}}>)}}""".format(uri)

    response = connection.run_query(q)

    n_check = response.json()
    if n_check['results']['bindings'][0]['u']:
        return True
    else:
        return False
