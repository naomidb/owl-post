import random
import requests
import urllib

from queries import check_n_value
from thing import Thing

class Connection(object):
    def __init__(self, vivo_url, check_url, user, password, u_endpoint, q_endpoint):
        self.user = user
        self.password = password
        self.update_endpoint = u_endpoint
        self.query_endpoint = q_endpoint
        self.vivo_url = vivo_url
        self.check_url = check_url
        '''res = requests.get(vivo_url)
        if res.code == 200:
            # we good
            self.vivo_url = vivo_url + 'individual/'
            pass
        else:
            exit('your vivo url is wrong')'''

    def check_n(self, n):
        # call to vivo, see if n number exists
        '''url = self.check_url + n
        page = requests.get(url).text
        title = page[page.find('<title>') + 7 : page.find('</title>')]
        return title == 'Individual Not Found'
        '''

        #create a Thing to test n number
        thing_check = Thing(self)
        thing_check.n_num = n
        params = {'the thing': thing_check}
        #use query to check if n number exists
        response = check_n_value.run(self, **params)
        return response

    def gen_n(self):
        bad_n = True
        while bad_n:
            # get an n
            n = "n" + str(random.randint(1,9999999999))
            # check if n is taken
            bad_n = self.check_n(n)
        return n

    def run_update(self, template):
        print("Query:\n" + template)
        payload = {
            'email': self.user,
            'password': self.password,
            'update': template
        }
        data = urllib.urlencode(payload)
        response = urllib.urlopen(self.update_endpoint, data)
        print "Status code:", response.code
        return response

    def run_query(self, template):
        print("Query:\n" + template)
        payload = {
            'email': self.user,
            'password': self.password,
            'query': template
        }
        url = self.query_endpoint
        headers = {'Accept': 'application/sparql-results+json'}
        response = requests.get(url, params=payload, headers=headers)
        
        #test = journal_dump['results']['bindings'][0]['label']['value']
        #print(test)
        #j = json.load(r)
        #print(j)
        
        #response = os.system("curl -i -d 'email={}' -d 'password={}' -d 'query={}' -H 'Accept: application/sparql-results+json' '{}' >> practice".format(self.user, self.password, template, self.query_endpoint))
        #with open('practice', 'w') as file:
         #   json.dump(response, file)
        return response
