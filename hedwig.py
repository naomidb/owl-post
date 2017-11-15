from bibtexparser import loads
import sys
import yaml

from owlery import Connection
import queries

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except Exception, e:
        print("Error: Check config file")
        print(e)
        exit()
    return config

def bib2csv(bib_data):
    csv_data = {}
    row = 0
    col_names = set(y for x in bib_data.entries for y in x.keys())

    for x in bib_data.entries:
        row += 1
        csv_data[row] = {}

        for col_name in col_names:
            v = x.get(col_name, '')
            v = v.replace('\n', ' ')
            v = v.replace('\r', ' ')
            v = v.replace('\t', ' ')
            csv_data[row][col_name] = v.encode('utf-8').strip()
    return csv_data

def process(connection, data):
    params = queries.make_academic_article.get_params(connection)
    article = params['Article']
    journal = params['Journal']

    #TODO: make sure 'type' is Article
    author_str = data['author']

    title = data['title']
    article_n = match_input(title, 'academic_article')
    if article_n:
        add_authors(connection, article, author_str)
        return
    article.title = title

    doi = data['doi']
    #match_input(doi, 'doi')
    article.doi = doi

    keyword = data['keyword']

    pages = data['pages']
    try:
        start, end = pages.split('-')
    except ValueError as e:
        start = pages
        end = None

    volume = data['volume']
    article.volume = volume

    year = data['year']
    article.publication_year = year

    #TODO: add journal filter
    #TODO: publisher filter
    journal_name = data['journal']   
    journal_n = match_input(journal_name, 'journal')
    if journal_n:
        journal.n_number = journal_n
    else:
        publisher_name = data['publisher']
        make_journal(connection, journal_name, publisher_name)    
        
    add_authors(connection, article, author_str)

def match_input(label, obj_type):
    #TODO: special match function for doi
    deets = queries.find_n_for_label.get_params()
    deets['Thing'].name = label
    deets['Thing'].category = obj_type

    current_list = queries.find_n_for_label.run(connection, **deets)
    choices = {}
    for key, val in current_list.items():
        if label.lower() == val.lower():
            choices[key] = val

    if len(choices) == 1:
        for key in choices:
            number = key
    else:
        #TODO: deal with duplicates
        number = None

    return number

    #TODO: make queries to just search for the match directly
    # deets = {}
    # search_query = "get_" + obj_type + "_list"
    # query_path = getattr(queries, search_query)
    # current_list = query_path.run(connection, **deets)

    # for key, val in current_list.items():
    #     if label.lower() == val.lower():
    #         choices[key] = val

    # if len(choices) == 1:
    #     return next(iter(choices))

def make_journal(connection, journal_name, publisher_name):
    #match_input(publisher_name, 'publisher')

def add_authors(connection, article, author_str):

def main(argv1):
    config_path = argv1
    config = get_config(config_path)

    email = config.get('email')
    password = config.get ('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')
    check_url = config.get('checking_url')
    input_file = config.get('input_file')

    connection = Connection(vivo_url, check_url, email, password, update_endpoint, query_endpoint)

    bib_str = ""
    with open (input_file, 'r') as bib:
        for line in bib:
            bib_str += line

    bib_data = loads(bib_str)
    csv_data = bib2csv(bib_data)

    for entry in csv_data.items():
        number, data = entry
        process(connection, data)
    
    #search if publication exists
    #search if journal exists
        #search if publisher exists
    #search if authors exist (be careful for initials)

if __name__ == '__main__':
    main(sys.argv[1])