import urllib

#Preexisitng authors are identified with n number
class Author():
    def __init__(self, data, connection, **kwargs):
        #for key, val in data.items():
            #setattr(self, key, val)
        self.connection = connection
        self.n = n
        for key, val in kwargs.items():
            if key == 'number':
                n = kwargs.get(key)
            else if key == 'email':
                n = find_n(kwargs.get(email))

        if self.is_extant():
            do something
        else:
            somthingelse
        if not n:
            self.create_n()

    def find_n(self, email):
        query='''
        SELECT ?person
        WHERE
        {
          ?person obo:ARG_2000028 ?o .
          ?o vcard:hasEmail ?email .
          ?email vcard:email ?name.
          FILTER (?name="{}"^^<http://www.w3.org/2001/XMLSchema#string>)
        }
        '''.format(email)
        author_id = self.connection.send_query(query)
        id_rest_stop = author_id.replace('<' + vivo_url + '/individual', '')
        n = id_rest_stop.replace('>', '')
        return n

    def create_n(self):
        self.n = connection.gen_n()

    def final_check(self, other_n):
        if self.n == other_n:
            self.n = connection.gen_n()
        return self.n