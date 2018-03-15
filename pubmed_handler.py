from pubmed_connect import PUBnnection
from vivo_queries.name_cleaner import clean_name

class Citation(object):
    def __init__(self, data):
        self.data = data

    def check_key(self, paths, data=None):
        if not data:
            data = self.data
        if paths[0] in data:
            trail = data[paths[0]]
            if len(paths) > 1:
                trail = self.check_key(paths[1:], trail)
            return trail
        else:
            return ""

class PHandler(object):
    def __init__(self, email):
        self.pubnnection = PUBnnection(email)

    def get_data(self, query):
        id_list = self.pubnnection.get_id_list(query)
        results = self.pubnnection.get_details(id_list)
        return results

    def parse_api(self, pm_dump):
        pubs = []
        pub_auth = {}
        authors = []
        journals = {}
        pub_journ = {}

        for citing in pm_dump['PubmedArticle']:
            citation = Citation(citing['MedlineCitation'])
            pub_title = clean_name(citation.check_key(['Article', 'ArticleTitle']))
            try:
                doi = str(citation.check_key(['Article', 'ELocationID'])[0])
            except IndexError as e:
                doi = ""
            year = citation.check_key(['Article', 'Journal', 'JournalIssue', 'PubDate', 'Year'])
            volume = citation.check_key(['Article', 'Journal', 'JournalIssue', 'Volume'])
            issue = citation.check_key(['Article', 'Journal', 'JournalIssue', 'Issue'])
            pages = citation.check_key(['Article', 'Pagination', 'MedlinePgn'])
            try:
                pub_type = str(citation.check_key(['Article', 'PublicationTypeList'])[0])
            except IndexError as e:
                doi = ""
            pmid = str(citation.check_key(['PMID']))
            issn = str(citation.check_key(['Article', 'Journal', 'ISSN']))
            journ_name = clean_name(citation.check_key(['Article', 'Journal', 'Title']))

            author_dump = citation.check_key(['Article', 'AuthorList'])
            for person in author_dump:
                author = Citation(person)
                lname = clean_name(author.check_key(['LastName']))
                fname = clean_name(author.check_key(['ForeName']))
                name = lname + ', ' + fname

                if name not in authors:
                    authors.append(name)

                if pmid not in pub_auth.keys():
                    pub_auth[pmid] = [name]
                else:
                    #pubmed does not have an id for authors
                    pub_auth[pmid].append(name)

            pubs.append((doi, pub_title, year, volume, issue, pages, pub_type, pmid))
            if issn not in journals.keys():
                journals[issn] = journ_name
            pub_journ[pmid] = issn

        return (pubs, pub_auth, authors, journals, pub_journ)

    def prepare_tables(self, c):
        print("Making tables")
        c.execute('''create table if not exists pubmed_pubs
                        (doi text, title text, year text, volume text, issue text, pages text, type text, pmid text unique, created_dt text not null, modified_dt text not null, written_by text not null)''')

        c.execute('''create table if not exists pubmed_authors
                        (author text unique)''')

        c.execute('''create table if not exists pubmed_journals
                        (issn text unique, title text, created_dt text not null, modified_dt text not null, written_by text not null)''')

        c.execute('''create table if not exists pubmed_pub_auth
                        (pmid text, auth text, unique (pmid, auth))''')

        c.execute('''create table if not exists pubmed_pub_journ
                        (pmid text, issn text, unique (pmid, issn))''')

    def local_add_pubs(self, c, pubs, source):
        print("Adding publications")
        timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for pub in pubs:
            pmid = pub[7]
            c.execute('SELECT * FROM pubmed_pubs WHERE pmid=?', (pmid,))
            rows = c.fetchall()

            if len(rows)==0:
                dataset = (pub + (timestamp, timestamp, source))
                c.execute('INSERT INTO pubmed_pubs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', dataset)
            else:
                for row in rows:
                    if row[0:8] != pub:
                        with open('log.txt', 'a+') as log:
                            log.write(timestamp + ' -- ' + 'pubmed_pubs' + '\n' + str(row) + '\n')
                        sql = '''UPDATE pubmed_pubs
                                    SET doi = %s ,
                                        title = %s ,
                                        year = %s ,
                                        volume = %s ,
                                        issue = %s ,
                                        pages = %s ,
                                        type = %s ,
                                        modified_dt = %s ,
                                        written_by = %s
                                    WHERE pmid = %s'''
                        c.execute(sql, (pub[0:7] + (timestamp, source, pub[7])))

    def local_add_authors(self, c, authors):
        print("Adding authors")
        for auth in authors:
            try:
                c.execute('INSERT INTO pubmed_authors VALUES(%s)', (auth,))
            except sqlite3.IntegrityError as e:
                pass

    def local_add_journals(self, c, journals, source):
        print("Adding journals")
        timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
        for issn, title in journals.items():
            c.execute('SELECT * FROM pubmed_journals WHERE issn=%s', (issn,))
            rows = c.fetchall()

            if len(rows)==0:
                c.execute('INSERT INTO pubmed_journals VALUES (%s, %s, %s, %s, %s)', (issn, title, timestamp, timestamp, source))
            else:
                for row in rows:
                    if row[0:2] != (issn, title):
                        with open('log.txt', 'a+') as log:
                            log.write(timestamp + ' -- ' + 'pubmed_journals' + '\n' + str(row) + '\n')
                        sql = '''UPDATE wos_journals
                                SET title = %s ,
                                    modified_dt = %s ,
                                    written_by = %s
                                WHERE issn = %s'''
                        c.execute(sql, (title, timestamp, source, issn))

    def local_add_pub_auth(self, c, pub_auth):
        print("Adding publication-author linkages")
        for pmid, auth_list in pub_auth.items():
            for auth in auth_list:
                try:
                    c.execute('INSERT INTO pubmed_pub_auth VALUES(%s, %s)', (pmid, auth))
                except sqlite3.IntegrityError as e:
                    pass

    def local_add_pub_journ(self, c, pub_journ):
        print("Adding publication-journal linkages")
        for pmid, issn in pub_journ.items():
            try:
                c.execute('INSERT INTO pubmed_pub_journ VALUES(%s, %s)', (pmid, issn))
            except sqlite3.IntegrityError as e:
                pass
