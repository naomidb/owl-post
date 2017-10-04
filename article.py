from VDO import VivoDomainObject

class Article(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "article"
        self.category = "publication"
        
        self.n_number = None
        self.title = None
        self.volume = None
        self.issue = None
        self.start_page = None
        self.end_page = None
        self.publication_year = None
        self.doi = None
        self.pubmed_id = None
        self.details = ['n_number', 'title', 'volume', 'issue', 'start_page', 'end_page', 'publication_year', 'doi', 'pubmed_id']

    # TODO: figure out why i wrote this here????
    # def get_matching_journals(self):
    #     params = {}
    #     journal_list = get_journals.run(self.connection, **params)

    #     journal_options = {}
    #     for key, val in journal_list.items():
    #         if self.journal == key:
    #             journal_options[key] = val

    #     return journal_options