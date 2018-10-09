import requests
import sqlite3
import sys
import yaml

from vivo_connect import Connection
from queries import get_person_list

def collect_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

# def acquire_authors(config):
#     vivonnection = Connection(config.get('upload_url'), config.get('email'), config.get('password'), config.get('update_endpoint'), config.get('query_endpoint'))
#     person_list = get_person_list.run(connection, {})
#     return person_list

def acquire_authors(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * from pubmed_authors')

    rows = c.fetchall()

    return rows

def peruse_pubmed(person_list):
    for person in person_list:
        x

def main(config_path):
    config = collect_config(config_path)
    #get list of pubmed uf authors
    person_list = acquire_authors(config)
    #attempt to find n_numbers for authors through vivo
    #create pmid list

if __name__ == '__main__':
    main(sys.argv[1])
