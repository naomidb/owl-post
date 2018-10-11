# docstr = """
# Hermes
# Usage:
#     hermes.py (-h | --help)
#     hermes.py (-a | -r) [-d] [-i] <config_file>

# Options:
#  -h --help        Show this message and exit
#  -a --api         Use VIVO api to upload data immediately
#  -r --rdf         Produce rdf files with data
#  -d --database    Put api results into MySQL database
#  -i --interact    Get query from user
# """

import datetime
import mysql.connector as mariadb
import os
import yaml

from vivo_utils import queries
from vivo_utils.connections.vivo_connect import Connection
from vivo_utils import vivo_log
from vivo_utils.triple_handler import TripleHandler
from vivo_utils.update_log import UpdateLog
from vivo_utils.handlers.pubmed_handler import PHandler

CONFIG_PATH = '<config_file>'
_api = '--api'
_rdf = '--rdf'
_db = '--database'
_interact = '--interact'

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except Exception as e:
        print("Error: Check config file")
        print(e)
        exit()
    return config

def search_pubmed(handler, log_file, interact):
    if interact:
        query = input("Enter your query: ")
    else:
        query = 'University of Florida[Affiliation] AND "last 2 days"[edat]'

    print("Searching pubmed")
    results = handler.get_data(query, log_file)

    return results

def check_filter(abbrev_filter, name_filter, name):
    try:
        if os.path.isfile(abbrev_filter):
            cleanfig = get_config(abbrev_filter)
            abbrev_table = cleanfig.get('abbrev_table')
            name += " " #Add trailing space
            name = name.replace('\\', '')
            for abbrev in abbrev_table:
                if (abbrev) in name:
                    name = name.replace(abbrev, abbrev_table[abbrev])
            name = name[:-1] #Remove final space

        if os.path.isfile(name_filter):
            namefig = get_config(name_filter)
            try:
                if name.upper() in namefig.keys():
                    name = namefig.get(name.upper())
            except AttributeError as e:
                name = name
    except TypeError:
        name = name

    return name

def process(connection, publication, added_journals, added_authors, tripler, ulog, db_name, filter_folder):
    abbrev_filter = os.path.join(filter_folder, 'general_filter.yaml')
    j_filter = os.path.join(filter_folder, 'journal_filter.yaml')
    # Add the journal
    journal_n = None
    if publication.journal:
        publication.journal = check_filter(abbrev_filter, j_filter, publication.journal)
        # Search for journal matches. Also check journals added this session.
        # If no matches, do a more lenient search. If no matches, match by issn.
        journal_matches = vivo_log.lookup(db_name, 'journals', publication.journal, 'name')
        if publication.journal in added_journals.keys():
            journal_matches.append([added_journals[publication.journal],])
        if len(journal_matches) == 0:
            journal_matches = vivo_log.lookup(db_name, 'journals', publication.journal, 'name', True)
            if len(journal_matches) == 0:
                journal_matches = vivo_log.lookup(db_name, 'journals', publication.issn, 'issn')
        if len(journal_matches) == 1:
            journal_n = journal_matches[0][0]
        else:
            journal_params = queries.make_journal.get_params(connection)
            journal_params['Journal'].name = publication.journal
            journal_params['Journal'].issn = publication.issn
            journal_params['Journal'].eissn = publication.eissn
            tripler.update(queries.make_journal, **journal_params)

            journal_n = journal_params['Journal'].n_number
            ulog.add_to_log('journals', publication.journal, (connection.namespace + journal_n))
            added_journals[publication.journal] = journal_n
            if len(journal_matches) > 1:
                jrn_n_list = [journal_n]
                for jrn_match in journal_matches:
                    jrn_n_list.append(jrn_match[0])
                ulog.track_ambiguities(publication.journal, jrn_n_list)

    pub_n = add_pub(connection, publication, journal_n, tripler, ulog, db_name)

    author_ns = []
    if publication.authors:
        for author in publication.authors.keys():
            orcid = publication.authors[author]
            if pub_n:
                author_n = add_authors(connection, author, orcid, added_authors, tripler, ulog, db_name)
                author_ns.append(author_n)
            else:
                ulog.add_author_to_skips(publication.pmid, author, orcid)

    if pub_n:
        if author_ns:
            add_authors_to_pub(connection, pub_n, author_ns, tripler)
        print("Pub added")

def add_pub(connection, publication, journal_n, tripler, ulog, db_name):
    pub_type = None
    query_type = None

    if 'Journal Article' in publication.types:
        pub_type = 'academic_article'
        query_type = getattr(queries, 'make_academic_article')
    elif 'Editorial' in publication.types:
        pub_type = 'editorial'
        query_type = getattr(queries, 'make_editorial_article')
    elif 'Letter' in publication.types:
        pub_type = 'letter'
        query_type = getattr(queries, 'make_letter')
    elif 'Abstract' in publication.types:
        pub_type = 'abstract'
        query_type = getattr(queries, 'make_abstract')
    else:
        query_type = 'pass'

    publication_matches = vivo_log.lookup(db_name, 'publications', publication.title, 'title')
    if len(publication_matches) == 0:
        publication_matches = vivo_log.lookup(db_name, 'publications', publication.doi, 'doi')
    if len(publication_matches) == 1:
        pub_n = publication_matches[0][0]
    else:
        pub_params = queries.make_academic_article.get_params(connection)
        pub_params['Journal'].n_number = journal_n
        pub_params['Article'].name = publication.title
        pub_params['Article'].volume = publication.volume
        pub_params['Article'].issue = publication.issue
        pub_params['Article'].publication_year = publication.year
        pub_params['Article'].doi = publication.doi
        pub_params['Article'].pmid = publication.pmid
        pub_params['Article'].start_page = publication.start_page
        pub_params['Article'].end_page = publication.end_page
        pub_params['Article'].number = publication.number

        if query_type=='pass':
            ulog.track_skips(publication.pmid, publication.types, **pub_params)
            pub_n = None
        else:
            tripler.update(query_type, **pub_params)
            pub_n = pub_params['Article'].n_number
            ulog.add_to_log('articles', publication.title, (connection.namespace + pub_n))

        if len(publication_matches) > 1:
            pub_n_list = []
            for pub_match in publication_matches:
                pub_n_list.append(pub_match[0])
            if pub_n:
                pub_n_list.append(pub_n)
            ulog.track_ambiguities(publication.title, pub_n_list)
    return pub_n

def parse_name(author):
    try:
        last, rest = author.split(', ')
        try:
            first, middle = rest.split(" ", 1)
            return (first, middle, last)
        except ValueError as e:
            first = rest
            return (first, '', last)
    except ValueError as e:
        last = author
        return ('', '', last)

def add_authors(connection, author, orcid, added_authors, tripler, ulog, db_name):
    first, middle, last = parse_name(author)

    matches = vivo_log.lookup(db_name, 'authors', author, 'display')
    if author in added_authors.keys():
        matches.append(added_authors[author])

    if len(matches) == 0:
        matches = vivo_log.lookup(db_name, 'authors', author, 'display', True)
    if len(matches) == 1:
        author_n = matches[0][0]
    else:
        params = queries.make_person.get_params(connection)
        params['Author'].name = author
        params['Author'].last = last
        if first:
            params['Author'].first = first
        if middle:
            params['Author'].middle = middle
        params['Author'].orcid = orcid
        tripler.update(queries.make_person, **params)

        author_n = params['Author'].n_number
        ulog.add_to_log('authors', author, (connection.namespace + author_n))
        added_authors[author] = author_n 
        if len(matches) > 1:
            auth_n_list = [author_n]
            for match in matches:
                auth_n_list.append(match[0])
            ulog.track_ambiguities(author, auth_n_list)
    return author_n

def add_authors_to_pub(connection, pub_n, author_ns, tripler):
    for author_n in author_ns:
        params = queries.add_author_to_pub.get_params(connection)
        params['Article'].n_number = pub_n
        params['Author'].n_number = author_n
        
        added = tripler.run_checks(queries.check_author_on_pub, **params)
        # added = queries.check_author_on_pub.run(connection, **params)
        if not added:
            tripler.update(queries.add_author_to_pub, **params)

def main(args):
    config = get_config(args[CONFIG_PATH])
    email = config.get('email')
    password = config.get ('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    namespace = config.get('namespace')
    filter_folder = config.get('filter_folder')

    db_name = '/tmp/vivo_temp_storage.db'

    connection = Connection(namespace, email, password, update_endpoint, query_endpoint)
    handler = PHandler(email)
    vivo_log.update_db(connection, db_name, ['authors', 'journals', 'publications'])

    try:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y_%m_%d")
        full_path = os.path.join(config.get('folder_for_logs'),
            now.strftime("%Y")+ '/' + now.strftime("%m") + '/' + now.strftime("%d"))
        try:
            os.makedirs(full_path)
        except FileExistsError:
            pass

        disam_file = os.path.join(full_path, (timestamp + '_pm_disambiguation.json'))
        output_file = os.path.join(full_path, (timestamp + '_pm_output_file.txt'))
        upload_file = os.path.join(full_path, (timestamp + '_pm_upload_log.txt'))
        skips_file = os.path.join(full_path, (timestamp + '_pm_skips.json'))

        results = search_pubmed(handler, output_file, args[_interact])
        publications = handler.parse_api(results)

        if args[_db]:
            db = config.get('database')
            db_port = config.get('database_port')
            db_user = config.get('database_user')
            db_pw = config.get('database_pw')
            sql_insert(db, db_port, db_user, db_pw, handler, pubs, pub_auth, authors, journals, pub_journ)

        meta = {'source': 'Hermes', 'harvest_date': now.strftime("%Y-%m-%d")}
        tripler = TripleHandler(args[_api], connection, meta, output_file)
        ulog = UpdateLog()

        added_journals = {}
        added_authors = {}
        for publication in publications:
            process(connection, publication, added_journals, added_authors, tripler, ulog, db_name, filter_folder)

        file_made = ulog.create_file(upload_file)
        ulog.write_skips(skips_file)
        ulog.write_disam_file(disam_file)

        if args[_rdf]:
            rdf_file = timestamp + '_upload.rdf'
            rdf_filepath = os.path.join(full_path, rdf_file)
            tripler.print_rdf(rdf_filepath)

        os.remove(db_name)
    except Exception:
        os.remove(db_name)
        import traceback
        exit(traceback.format_exc())

# if __name__ == '__main__':
#     args = docopt(docstr)
#     main(args)