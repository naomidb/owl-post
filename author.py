import urllib
from VDO import VivoDomainObject

class Author(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "author"
        self.category = "person"

        self.n_number = None
        self.name = None
        self.details = ['n_number', 'name']