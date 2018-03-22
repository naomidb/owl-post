import sqlite3
import sys
from time import localtime, strftime
import yaml

from vivo.queries.vivo_connect import Connection
from vivo_queries import queries
from vivo_queries.triple_handler import TripleHandler

#pub order is: doi, title, year, volume, issue, pages, doctype, number

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

def find_john_does(db_path, c):
    c.execute('SELECT * FROM vivo_pubs where doi=""')
    orphans = c.fetchall()

    return orphans

def get_fuzzy_pub_matches(pub, c):
    title = pub[1]

    c.execute('SELECT title, wosid FROM wos_pubs')
    wos_list = c.fetchall()

    c.execute('SELECT title, pmid FROM pubmed_pubs')
    pubmed_list = c.fetchall()



def get_more_details(pub, c):
    nnum = pub[7]

    #get journals
    c.execute('SELECT j.issn, j.title FROM vivo_journals as j WHERE j.journ_num in (SELECT pj.journ_num FROM vivo_pub_journ as pj WHERE pub_num=?)', (nnum,))
    journal_info = c.fetchall()

    #get authors
    c.execute('SELECT a.author_name FROM vivo_authors as a WHERE author in (SELECT pa.auth FROM vivo_pub_auth as pa WHERE pub_num=?', (nnum,))
    authors = c.fetchall()

    return (journal_info, authors)

def find_matches(pub, journal_info, authors, c):
    same_journal_pubs = match_journal(journal_info, c)

def match_journal(journal, c):
    issn = journal[0]
    j_title = journal[1]
    #check wos for perfect matches
    if issn:
        c.execute('SELECT * FROM wos_pubs as p WHERE p.wosid=(SELECT j.wosid FROM wos_pub_journ as j WHERE j.issn=?)', (issn,))
    else:
        c.execute('SELECT * FROM wos_pubs as p WHERE p.wosid in (SELECT pj.wosid FROM wos_pub_journ as pj WHERE pj.issn in (SELECT j.issn FROM wos_journals as j WHERE j.title=?))', (j_title,))

    pub_list = c.fetchall()

    if not pub_list:
        #check pubmed for perfect matches
        if issn:
            c.execute('SELECT * FROM pubmed_pubs as p WHERE p.pmid=(SELECT j.pmid FROM pubmed_pub_journ as j WHERE j.issn=?)', (issn,))
        else:
            c.execute('SELECT * FROM pubmed_pubs as p WHERE p.pmid in (SELECT pj.pmid FROM pubmed_pub_journ as pj WHERE pj.issn in (SELECT j.issn FROM pubmed_journals as j WHERE j.title=?))', (j_title,))

        pub_list = c.fetchall()

    return pub_list

def match_author():
    x

def identify_pubs(config):
    vivonnection = Connection(config.get('upload_url'), config.get('email'), config.get('password'), config.get('update_endpoint'), config.get('query_endpoint'))

def main(config_path, db_path):
    config = get_config(config_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    orphans = find_john_does(db_path, c)

    for pub in orphans:
        journal_info, authors = get_more_details(pub, c)
        best_match = find_matches(pub, journal_info, authors, c)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
