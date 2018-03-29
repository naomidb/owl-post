class TripleStore(object):
    def __init__(self):
        self.triples = []

    def search_for_label(self, label):
        label = '"' + label + '"'
        for trip in self.triples:
            if label in trip:
                #get existing n number
                uri = trip.split('>', 1)[0]
                number = uri.rsplit('/', 1)[-1]
                return number
        return None

    def add_triple(self, sentence):
        self.triples.append(sentence)

    def write_to_file(self, filepath):
        with open(filepath, 'w') as output:
            for triple in self.triples:
                output.write(triple + '\n')