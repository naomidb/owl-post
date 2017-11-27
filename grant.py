from VDO import VivoDomainObject


class Grant(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "grant"
        self.category = "grant"

        self.n_number = None
        self.name = None
        self.abstract = None
        self.start_date = None
        self.end_date = None
        self.details = ['name', 'abstract', 'start_date', 'end_date']
