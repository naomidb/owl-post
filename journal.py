class Journal(object):
    def __init__(self, connection):
        self.connection = connection
        self.type = "journal"
        
        self.n_num = None
        self.title = None
        self.details = ['title']

    def get_details(self):
        return self.details

    def create_n(self):
        self.n_num = self.connection.gen_n()

    def final_check(self, other_n):
        if self.n_num == other_n:
            self.n_num = self.connection.gen_n()
        return self.n_num