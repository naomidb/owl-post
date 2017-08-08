from article import Article
from author import Author
from owlery import Connection
import queries

def create_query(build, connection, **kwargs):
    response = run(connection, **kwargs)
    return response

def main(email, password, identifier):
    email = config.get('email')
    password = config.get ('password')
    endpoint = config.get('endpoint')
    vivo_url = config.get('upload_url')
    check_url = config.get('checking_url')

    connection = Connection(vivo_url, check_url, email, password, endpoint)

    #identifier = {'number': 'n7784'}
    author = Author(connection, **identifier)
    print ("author made")
    article = Article(connection)
    print ("article made")

    build = queries.make_pub_existing_author.build
    print("build established")
    response = create_query(build, connection, author=author, article=article)