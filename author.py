import urllib
from VDO import VivoDomainObject

class Author(VivoDomainObject):
    def __init__(self, connection):
        self.connection = connection
        self.type = "person"
        self.category = "person"

        self.n_number = None
        self.name = None
        self.first = None
        self.middle = None
        self.last = None
        self.email = None
        self.phone = None
        self.title = None
        self.details = ['email', 'phone', 'title']