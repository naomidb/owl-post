from owlery import Connection
from author import Author
from article import Article

def create_query(request, connection, **kwargs):
    from queries import request
    query = request.build(**kwargs)
    return query

def main():
    email = 'vivo_root@school.edu'
    password = 'FreeLunch'
    endpoint = 'http://localhost:8080/vivo/api/sparqlUpdate'
    vivo_url = 'http://vivo.school.edu/individual/'
    connection = Connection(vivo_url, email, password, endpoint)

    author = Author(connection, number: 'n7784')
    article = Article(connection)

    request = make_pub_pre-existing_author
    query = create_query(request, connection, author, article)

    response = connection.run_query(query)

if __name__ == '__main__':
    main()