class Article(object):
    def __init__(self, connection, existant):
        self.connection = connection
        self.type = "article"
        
        if existant:
            self.n_num = None
            self.details = ['n_num']
        else:
            self.n_num = None
            print("Gotta make an n")
            self.create_n()

            self.title = None
            self.volume = None
            self.issue = None
            self.start_page = None
            self.end_page = None
            self.details = ['title', 'volume', 'issue', 'start_page', 'end_page']

    def get_details(self):
        return self.details

    def create_n(self):
        self.n_num = self.connection.gen_n()

    def get_matching_journals(self):
        params = {}
        journal_list = get_journals.run(self.connection, **params)

        journal_options = {}
        for key, val in journal_list.items():
            if self.journal == key:
                journal_options[key] = val

        return journal_options
    
    def final_check(self, other_n):
        if self.n_num == other_n:
            self.n_num = self.connection.gen_n()
        pass

