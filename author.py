import urllib

#Preexisitng authors are identified with n number
class Author(object):
    def __init__(self, connection):
        #for key, val in data.items():
            #setattr(self, key, val)
        self.connection = connection
        self.type = "author"

        self.n_num = None
        self.name = None
        self.details = ['n_num', 'name']

    def get_details(self):
        return self.details

    def create_n(self):
        self.n = connection.gen_n()

    def final_check(self, other_n):
        if self.n_num == other_n:
            self.n_num = connection.gen_n()
        return self.n_num

        # for key, val in kwargs.items():
        #     if key == 'author_n':
        #         self.n = kwargs.get(key)
        #     elif key == 'author_email':
        #         self.n = find_n(kwargs.get(key))

        # print(self.n)
        '''if self.is_extant():
            do something
        else:
            somthingelse
        if not n:
            self.create_n()'''

    # def find_n(self, email):
    #     query='''
    #     SELECT ?person
    #     WHERE
    #     {
    #       ?person obo:ARG_2000028 ?o .
    #       ?o vcard:hasEmail ?email .
    #       ?email vcard:email ?name.
    #       FILTER (?name="{}"^^<http://www.w3.org/2001/XMLSchema#string>)
    #     }
    #     '''.format(email)
    #     author_id = self.connection.run_query(query)
    #     id_rest_stop = author_id.replace('<' + vivo_url + '/individual', '')
    #     n = id_rest_stop.replace('>', '')
    #     return n