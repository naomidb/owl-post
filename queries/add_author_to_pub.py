from article import Article
from author import Author

def get_params(connection):
    article = new Article(connection)
    author = new Author(connection)
    params = {'Article': article, 'Author': author}
    return params

def run(connection, **params):
    relationship_id = connection.gen_n()
    relation_url = connection.vivo_url + relationship_id
    article_url = connection.vivo_url + params['Article'].n_number
    author_url = connection.vivo_url + params['Author'].n_number

    q = """
        INSERT DATA {{
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
            {{
                <{relation_url}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship> .
                <{relation_url}> <http://vivoweb.org/ontology/core#relates> <{article_url}> .
                <{relation_url}> <http://vivoweb.org/ontology/core#relates> <{author_url}> .
                <{article_url}> <http://vivoweb.org/ontology/core#relatedBy> <{relation_url}> .
            }}
        }}
    """