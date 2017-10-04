from VDO import VivoDomainObject

class Thing(object):
    def __init__(self, connection):
        self.connection = connection
        self.type = "thing"

        self.n_number = None
        self.details = ['n_number']