class Journal(object):
    def __init__(self, connection, existant):
        self.connection = connection
        self.type = "journal"
        
        if existant:
            self.n_num = None
            self.details = ['n_num']
        else:
            self.n_num = None
            self.title = None
            self.details = ['title']

    def get_details(self):
        return self.details

    def create_n(self):
        self.n = connection.gen_n()

    def final_check(self, other_n):
        if self.n == other_n:
            self.n = connection.gen_n()
        return self.n