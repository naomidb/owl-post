from jinja2 import Environment

from grant import Grant


def get_params(connection):
    grant = Grant(connection)
    params = {'Grant': grant}
    return params


def run(connection, **params):
    params['Grant'].create_n()
    params['upload_url'] = connection.vivo_url

    if params['Grant'].start_date:
        params['start_date_id'] = connection.gen_n()
    #        while (params['name_id'] in {params['Author'].n_number, params['vcard']}):
    #            params['name_id'] = connection.gen_n()

    if params['Grant'].end_date:
        params['end_date_id'] = connection.gen_n()

    q = Environment().from_string("""\
        INSERT DATA {
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
            {
                <{{upload_url}}{{Grant.n_number}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Grant> .
                <{{upload_url}}{{Grant.n_number}}> <http://www.w3.org/2000/01/rdf-schema#label> "{{Grant.name}}" .
                
              {%- if Grant.abstract %}
                <{{upload_url}}{{Grant.n_number}}> <http://purl.org/ontology/bibo/abstract> "{{Grant.abstract}}" .
              {%- endif -%}

            }
        }
        """)

    print('=' * 20 + "\nCreating new person\n" + '=' * 20)
    response = connection.run_update(q.render(**params))
    return response