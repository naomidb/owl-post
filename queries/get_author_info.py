from author import Author
from queries import get_vcard

def get_params(connection):
    author = Author(connection)
    params = {'Author': author}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Author'].n_number
    vcard = get_vcard.run(connection, **params)
    #response = {'phone': , 'email': , 'title': }

    q = """ SELECT ?phone ?email ?title ?overview ?geofocus
            WHERE {{
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#hasTelephone> ?puri . ?puri <http://www.w3.org/2006/vcard/ns#telephone> ?phone . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#hasEmail> ?euri . ?euri <http://www.w3.org/2006/vcard/ns#email> ?email . }}
                OPTIONAL {{ <{vcard}> <http://www.w3.org/2006/vcard/ns#hasTitle> ?turi . ?turi <http://www.w3.org/2006/vcard/ns#title> ?title . }}
                OPTIONAL {{ <{subj} <http://vivoweb.org/ontology/core#overview> ?overview . }}
                OPTIONAL {{ <{subj}> <http://vivoweb.org/ontology/core#geographicFocus> ?geofocus . }}                
            }}""".format(subj = subj, vcard = vcard)
    phone_res = connection.run_query(q)

    finding = phone_res.json()
    print(finding)
    #phone_id = finding['results']['bindings'][0]['phone']['value']