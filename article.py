class Article(object):
    def __init__(self, connection, existant):
        self.connection = connection
        self.type = "article"
        
        if existant:
            self.n_num = None
            self.details = ['n_num']
        else:
            self.n_num = None
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

    def check_journals(self, journal_input):
        params = (1,2)
        journal_list = get_journals.run(self.connection, *params)

        journal_options = {}
        for key, val in journal_list.items():
            if journal_input == key:
                journal_options[key] = val

        return journal_options
    
    def final_check(self, other_n):
        if self.n_num == other_n:
            self.n_num = self.connection.gen_n()
        pass

