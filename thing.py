class Thing(object):
    def __init__(self, connection):
        self.connection = connection
        self.type = "thing"

        self.n_num = None
        self.details = ['n_num']

    def get_details(self):
        return self.details