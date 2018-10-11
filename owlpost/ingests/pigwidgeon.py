cdocstr = """
Pigwidgeon
Usage:
    pigwidgeon.py (-h | --help)
    pigwidgeon.py (-a | -r) <config_file>

Options:
 -h --help        Show this message and exit
 -a --api         Use VIVO api to upload data immediately
 -r --rdf         Produce rdf files with data
 """

from docopt import docopt
import os.path
import sys
import datetime
import yaml

from vivo_utils.vdos.article import Article
from vivo_utils.vdos.author import Author
from vivo_utils.vdos.journal import Journal
from vivo_utils.handlers.pubmed_handler import Citation, PHandler
from vivo_utils import queries
from vivo_utils.connections.vivo_connect import Connection
from vivo_utils.triple_handler import TripleHandler
from vivo_utils.update_log import UpdateLog

CONFIG_PATH = '<config_file>'
_api = '--api'
_rdf = '--rdf'

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

def make_folders(top_folder, sub_folders=None):
    if not os.path.isdir(top_folder):
        os.mkdir(top_folder)

    if sub_folders:
        sub_top_folder = os.path.join(top_folder, sub_folders[0])
        top_folder = make_folders(sub_top_folder, sub_folders[1:])

    return top_folder

def identify_author(connection, tripler, ulog):
    author = Author(connection)
    obj_n = input("Enter the n number of the person (if you do not know, leave blank): ")
    if obj_n:
        author.n_number = obj_n
    else:
        print("Enter the person's name.")
        first_name = input("First name: ")
        if first_name:
            author.first = first_name
        middle_name = input("Middle name: ")
        if middle_name:
            author.middle = middle_name
        last_name = input("Last name: ")
        if last_name:
            author.last = last_name
        obj_name = last_name + ", " + first_name + " " + middle_name
        author.name = obj_name

        match = match_input(tripler, connection, obj_name, 'person', True)

        if not match:
            create_obj = input("This person is not in the database. Would you like to add them? (y/n) ")
            if create_obj == 'y' or create_obj == 'Y':
                print("Fill in the following details. Leave blank if you do not know what to write.")
                details = author.get_details()
                for detail in details:
                    item_info = input(str(detail) + ": ")
                    setattr(author, detail, item_info)

                params = {'Author': author}
                result = tripler.update(queries.make_person, **params)
                ulog.add_to_log('authors', author.name, (connection.namespace + params['Author'].n_number))
                print('*' * 6 + '\nAdding person\n' + '*' * 6)

    return author

def sort_articles(connection, pub, author, tripler, ulog):
    #TODO: add reviews
    citation = Citation(pub['MedlineCitation'])
    try:
        obj_type = str(citation.check_key(['Article', 'PublicationTypeList'])[0])
    except IndexError as e:
        obj_type = "Journal Article"

    article = Article(connection)
    article.name = scrub(citation.check_key(['Article', 'ArticleTitle']).title())
    article.volume = citation.check_key(['Article', 'Journal', 'JournalIssue', 'Volume'])
    article.issue =  citation.check_key(['Article', 'Journal', 'JournalIssue', 'Issue'])
    article.publication_year =  citation.check_key(['Article', 'Journal', 'JournalIssue', 'PubDate', 'Year'])
    pages = str(citation.check_key(['Article', 'Pagination', 'MedlinePgn']))
    try:
        start_page, end_page = pages.split("-")
        article.start_page = start_page
        article.end_page = end_page
    except ValueError as e:
        start_page = pages
        article.start_page = start_page

    try:
        article.doi =  str(citation.check_key(['Article', 'ELocationID'])[0])
    except IndexError as e:
        pass
    article.pmid =  citation.check_key(['PMID'])

    journal = get_journal(connection, citation, tripler, ulog)

    if obj_type=='Journal Article':
        #check if article exists
        match = match_input(tripler, connection, article.name, article.type, False)    #check with article title
        if not match:
            if article.doi:
                match = match_input(tripler, connection, article.doi, article.type, False) #check with article doi
            if not match:
                params = {'Article': article, 'Author': author, 'Journal': journal}
                result = tripler.update(queries.make_academic_article, **params)
                ulog.add_to_log('articles', article.name, (connection.namespace + article.n_number))
                print('*' * 6 + '\nAdding article\n' + '*' * 6)

    elif obj_type=='Editorial':
        article.type = 'editorial'
        match = match_input(tripler, connection, article.name, article.type, False)    #check with article title
        if not match:
            if article.doi:
                match = match_input(tripler, connection, article.doi, article.type, False) #check with article doi
            if not match:
                params = {'Article': article, 'Author': author, 'Journal': journal}
                result = tripler.update(queries.make_editorial_article, **params)
                ulog.add_to_log('articles', article.name, (connection.namespace + article.n_number))
                print('*' * 6 + '\nAdding article\n' + '*' * 6)

    elif obj_type=='Letter':
        article.type='letter'
        match = match_input(tripler, connection, article.name, article.type, False)    #check with article title
        if not match:
            if article.doi:
                match = match_input(tripler, connection, article.doi, article.type, False) #check with article doi
            if not match:
                params = {'Article': article, 'Author': author, 'Journal': journal}
                result = tripler.update(queries.make_letter, **params)
                ulog.add_to_log('articles', article.name, (connection.namespace + article.n_number))
                print('*' * 6 + '\nAdding article\n' + '*' * 6)

    else:
        match = match_input(tripler, connection, article.name, 'thing', False)
        if match:
            print('PMID ' + article.pmid + ' found at ' + match + '\n\n')
        else:
            pages = citation.check_key(['Article', 'Pagination', 'MedlinePgn'])
            try:
                start, end = pages.split('-')
            except ValueError as e:
                start = pages
                end = None
            params = {'Article': article, 'Journal': journal}
            ulog.track_skips(article.pmid, str(obj_type), **params)

def scrub(label):
    clean_label = label.replace('"', '\\"')
    return clean_label

def get_journal(connection, citation, tripler, ulog):
    parts = queries.make_journal.get_params(connection)
    parts['Journal'].name = citation.check_key(['Article', 'Journal', 'Title']).title()
    parts['Journal'].issn = str(citation.check_key(['Article', 'Journal', 'ISSN']))

    match = match_input(tripler, connection, parts['Journal'].name, 'journal', False)     #check with journal name
    if not match and parts['Journal'].issn:
        match = match_input(tripler, connection, parts['Journal'].issn, 'journal', False) #check with journal issn

    if match:
        parts['Journal'].n_number = match
    else:
        match = tripler.search_for_label(parts['Journal'].name)
        if match:
            parts['Journal'].n_number = match
        else:
            result = tripler.update(queries.make_journal, **parts)
            ulog.add_to_log('journals', parts['Journal'].name, (connection.namespace + parts['Journal'].n_number))
            print('*' * 6 + '\nAdding journal\n' + '*' * 6)

    return parts['Journal']

def match_input(tripler, connection, label, category, interact=False):
    details = queries.find_n_for_label.get_params(connection)
    details['Thing'].name = label
    details['Thing'].extra = label
    details['Thing'].type = category

    try:
        matches = queries.find_n_for_label.run(connection, **details)

        hits = {}
        match = None

        #no matches
        if (len(matches) == 0):
            #label is passed with doi. this counts on there being no articles with the doi as their name.
            if category == "academic_article":
                hits = queries.find_n_for_doi.run(connection, **details)
                if len(hits) == 1:
                    for key in hits:
                        match = key

            #label is passed with issn. this counts on there being no journals with the issn as their name.
            elif category == "journal":
                hits = queries.find_n_for_issn.run(connection, **details)
                if len(hits) == 1:
                    for key in hits:
                        match = key

            else:
                match = None

        #single match using title
        elif len(matches) == 1:
            for key in matches:
                match = key

        #multiple matches
        else:
            if interact:
                choices = {}
                count = 1
                for n_id, name in hits.items():
                    if label.lower in val.lower():
                        choices[count] = (n_id, name)
                        count += 1

                index = -1
                for key, val in choices.items():
                    number,label = val
                    print((str(key) + ': ' + label + ' (' + number + ')\n'))

                index = input("Do any of these match your input? (if none, write -1): ")
                if not index == -1:
                    nnum, label = choices.get(index)
                    match = nnum
                else:
                    match = None
            else:
                match = None
                #TODO: deal with duplicates
        return match
    except Exception as e:
        print(e)
        timestamp = strftime("%Y_%m_%d_%H_%M")
        filename = timestamp + '_upload.rdf'
        filepath = '/Users/looseymoose/Desktop/' + filename
        tripler.write_to_file(filepath)
        print('Check ' + filepath)
        exit()

def main(args):
    config = get_config(args[CONFIG_PATH])
    email = config.get('email')
    password = config.get('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    namespace = config.get('namespace')
    filter_folder = config.get('filter_folder')

    db_name = '/tmp/vivo_temp_storage.db'

    connection = Connection(namespace, email, password, update_endpoint, query_endpoint)
    vivo_log.update_db(connection, db_name)
    handler = PHandler(email)

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M")
    full_path = make_folders(config.get('folder_for_logs'), [now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")])

    output_file = os.path.join(full_path, (timestamp + '_pig_output_file.txt'))
    upload_file = os.path.join(full_path, (timestamp + '_pig_upload_log.txt'))
    skips_file = os.path.join(full_path, (timestamp + '_pig_skips_.json'))
    
    tripler = TripleHandler(args[_api], connection)
    ulog = UpdateLog()
    
    author = identify_author(connection, tripler, ulog)
    
    query = input("Write your pubmed query: ")
    raw_articles = handler.get_data(query)

    for citing in raw_articles['PubmedArticle']:
        sort_articles(connection, citing, author, tripler, ulog)

    are_uploads = ulog.create_file(upload_file)
    ulog.write_skips(skips_file)

    if args[_rdf]:
        rdf_file = timestamp + '_upload.rdf'
        rdf_filepath = os.path.join(full_path, rdf_file)
        tripler.print_rdf(rdf_filepath)
        print('Check ' + rdf_filepath)

if __name__ == '__main__':
    args = docopt(docstr)
    main(args)
