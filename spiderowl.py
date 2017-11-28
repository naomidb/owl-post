import subprocess

class WOSnnection(object):
    def __init__(self, config):
        self.token = None
        self.credentials = config.get('b64_credentials')

    def get_token(self):
        result = subprocess.check_output('curl -H "Authorization: Basic {}" -d "@wos/msg.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate"'.format(self.credentials))
        # os.system('curl -H "Authorization: Basic {}" -d "@msg.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate"').format(self.credentials)
        print(result)
        treasure = result[0][0][0][0]
        print(treasure)

        self.token = result