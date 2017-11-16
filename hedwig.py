from bibtexparser import loads
import sys
import yaml

from owlery import Connection
import queries

ARTICLE_COUNT = 0
JOURNAL_COUNT = 0
PUBLISHER_COUNT = 0
AUTHOR_COUNT = 0

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
    article_n = match_input(connection, title, 'academic_article') 
    if article_n:
        #article already exists
        add_authors(connection, article, author_str)
        return
    article.title = title

    doi = data['doi']
    #match_input(connection, doi, 'doi')
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
    clean_jname = check_journal_filter(journal_name)
    journal_n = match_input(connection, clean_jname, 'journal')
    if journal_n:
        journal.n_number = journal_n
    else:
        publisher_name = data['publisher']
        create_journal(connection, journal_name, publisher_name)    
    
    response = queries.make_academic_article.run(connection, **params)
    if response:
        AUTHOR_COUNT += 1    
    add_authors(connection, article, author_str)

def match_input(connection, label, obj_type):
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
            return key
    else:
        #TODO: deal with duplicates
        return None

def match_authors(connection, label):
    deets = queries.find_n_for_label.get_params()
    deets['Thing'].name = label
    deets['Thing'].category = 'author'

    current_list = queroes.find_n_for_label.run(connection, **deets)
    choices = {}
    #perfect match
    for key, val in current_list.items():
        if label.lower() = val.lower():
            choices[key] = val

    if len(choices) == 1:
        for key in choices:
            return key

    #match contains label
    if len(choices) == 0:
        for key, val in current_list.items():
            if label.lower() in val.lower():
                choices[key] = val

        if len(choices) == 1:
            for key in choices:
                return key

    #check against wos
    if len(choices) > 1:
        #stuff

def check_journal_filter(label):
    #primary cleaning

    #match against filter

    return clean_label

def create_journal(connection, journal_name, publisher_name):
    clean_pname = check_publisher_filter(publisher_name)
    publisher_n = match_input(connection, clean_pname, 'publisher')

    reqs = queries.make_journal.get_params(connection)
    reqs['Journal'].name = journal_name
    if publisher_n:
        reqs['Publisher'].n_number = publisher_n
    else:
        reqs['Publisher'].name = publisher_name
        PUBLISHER_COUNT += 1

    response = queries.make_journal.run(connection, **reqs)
    if response:
        JOURNAL_COUNT += 1
    print(response)

def add_authors(connection, article, author_str):
    authors = author_str.split(" and")
    for person in authors:
        args = queries.add_author.get_params(connection)
        author_n = match_input(connection, person)
        args['Author'].n_number = author_n
        args['Article'].n_number = article.n_number

        response = queries.add_author.run(connection, **args)
        if response:
            AUTHOR_COUNT += 1
        print(response)


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

    print("Summary of new items:\n  >Articles: " + ARTICLE_COUNT + "\n  >Journals: " + JOURNAL_COUNT + "\n  >Publishers: " + PUBLISHER_COUNT + "\n  >People: " + AUTHOR_COUNT)
if __name__ == '__main__':
    main(sys.argv[1])