class Article():
    def __init__(self, connection, label, n=None):
        print("Article creation")
        self.connection = connection
        self.label = label
        self.n = n
        print (n)
        if not n:
            #for key, val in kwargs.items():
                #if key == 'label':
                    #dosomething(val)
            self.n = connection.gen_n()
            print (self.n)
            #self.label = input("What is the name of this article? (please put quotation marks around the title) ")

    def final_check(self, other_n):
        if self.n == other_n:
            self.n = self.connection.gen_n()
        pass

