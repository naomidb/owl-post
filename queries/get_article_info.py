from article import Article

def get_params(connection):
    article = Article(connection)
    params = {'Article': article}
    return params

def run(connection, **params):
    subj = connection.vivo_url + params['Article'].n_number

    q = """ SELECT ?title ?volume ?issue ?start ?finish ?year ?doi ?pmid ?journal ?journal_name ?author
            WHERE {{
                OPTIONAL {{ <{subj}> <http://www.w3.org/2000/01/rdf-schema#label> ?title . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/volume> ?volume . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/issue> ?issue . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/pageStart> ?start . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/pageEnd> ?finish . }}
                OPTIONAL {{ <{subj}> <http://vivoweb.org/ontology/core#dateTimeValue> ?duri . ?duri <http://vivoweb.org/ontology/core#dateTime> ?year . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/doi> ?doi . }}
                OPTIONAL {{ <{subj}> <http://purl.org/ontology/bibo/pmid> ?pmid . }}
                OPTIONAL {{ <{subj}>  <http://vivoweb.org/ontology/core#hasPublicationVenue> ?journal . ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_name .}}
            }}""".format(subj = subj)
    response = connection.run_query(q)
    print(response)
    finding = response.json()

    title = parse_json(finding, 'title')
    volume = parse_json(finding, 'volume')
    issue = parse_json(finding, 'issue')
    start = parse_json(finding, 'start')
    finish = parse_json(finding, 'finish')
    year = parse_json(finding, 'year')
    doi = parse_json(finding, 'doi')
    pmid = parse_json(finding, 'pmid')
    journal_id = parse_json(finding, 'journal')
    journal_name = parse_json(finding, 'journal_name')

    info = {'title': title, 'volume': volume, 'issue': issue, 'start page': start, 'end page': finish, 'year': year, 'doi': doi, 'pmid': pmid, 'journal': journal_name, 'journal_n': journal_id}
    return info

def parse_json(finding, search):
    try:
        value = finding['results']['bindings'][0][search]['value']
    except KeyError as e:
        value = ''

    return value
