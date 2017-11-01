from VDO import VivoDomainObject

class Article(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "academic_article"
        self.category = "publication"
        
        self.n_number = None
        self.name = None
        self.volume = None
        self.issue = None
        self.start_page = None
        self.end_page = None
        self.publication_year = None
        self.doi = None
        self.pubmed_id = None
        self.details = ['volume', 'issue', 'start_page', 'end_page', 'publication_year', 'doi', 'pubmed_id']