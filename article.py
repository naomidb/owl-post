class Article():
    def __init__(self, connection, n=None, **kwargs):
        """

        """
        self.label
        self.connection = connection
        self.n = n
        if not n:
            for key, val in kwargs.items():
                if key == 'label':
                    dosomething(val)
            #self.create_n()

    def create_n(self):
        self.n = connection.gen_n()

    def final_check(self, other_n):
        if self.n == other_n:
            self.n = connection.gen_n()
        return self.n

