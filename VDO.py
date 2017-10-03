def VivoDomainObject(object):
    def __init__(self):
        return

    def get_details(self):
        return self.details

    def create_n(self):
        self.n = connection.gen_n()

    def final_check(self, other_n):
        if self.n_num == other_n:
            self.n_num = connection.gen_n()
        return self.n_num