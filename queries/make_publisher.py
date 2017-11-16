from publisher import Publisher

def get_params(connection):
    publisher = Publisher(connection)
    params = {'Publisher': publisher}
    return params

def run(connection, **params):
    publisher = params.get('Publisher')
    upload_url = connection.vivo_url

    if publisher.n_number == None:
        publisher.create_n()

    q = """
    INSERT DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
        {{
            <{url}{Publisher.n_number}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Publisher> .
            <{url}{Publisher.n_number}> <http://www.w3.org/2000/01/rdf-schema#label> "{Publisher.name}" .
        }}
    }}
    """.format(url=upload_url ,Publisher=publisher)

    print('=' * 20 + "\nCreating new publisher\n" + '=' * 20)
    response = connection.run_update(q)
    return response