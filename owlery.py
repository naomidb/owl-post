import requests
import random

class Connection(object):
    def __init__(self, vivo_url, user, password, endpoint):
        self.user = user
        self.password = password
        self.endpoint = endpoint
        res = get(vivo_url)
        if res.code == 200:
            # we good
            self.vivo_url = vivo_url
            pass
        else:
            exit('your vivo url is wrong')

    def check_n(self, n):
        # call to vivo, see if n number exists
        page = requests.get(self.vivo_url).text
        title = page[page.find('<title>') + 7 : page.find('</find>')]
        return title != 'Individual Not Found'

    def gen_n(self):
        good_n = False
        while not good_n:
            # get an n
            n = str(random.randint(1,9999999999))
            # check if good
            self.check_n(n)
        return n

    def run_query(self, query):
        print "Query:\n" + query
        payload = {
            'email': self.user,
            'password': self.password,
            'update': query
        }
        data = urllib.urlencode(payload)
        response = urllib.urlopen(self.endpoint, data)
        print "Status code:", response.code
        return response
        pass