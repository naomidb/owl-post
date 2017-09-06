from author import Author
from article import Article
from journal import Journal

def get_params(connection):
    author = Author(connection, True)
    article = Article(connection, False)
    journal = Journal(connection)
    params = {'Author': author, 'Article': article, 'Journal': journal}
    return params


def run(connection, **params):
    # check for valid data
    for title, item in params.items():
        if item.type == 'author':
            author = item
        elif item.type == 'article':
            article = item
        elif item.type == 'journal':
            journal = item
    relationship_id = connection.gen_n()
    article.final_check(relationship_id)
    article.final_check(journal.n_num)

    # template data into q
    q = """
    INSERT DATA {{
       GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> 
       {{
            <http://vivo.school.edu/individual/{Article.n_num}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle>  .
            <http://vivo.school.edu/individual/{Relationship}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship>  .
            <http://vivo.school.edu/individual/{Relationship}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{Article.n_num}> .
            <http://vivo.school.edu/individual/{Relationship}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{Author.n_num}> .
            <http://vivo.school.edu/individual/{Article.n_num}> <http://vivoweb.org/ontology/core#relatedBy> <http://vivo.school.edu/individual/{Relationship}> .
            <http://vivo.school.edu/individual/{Article.n_num}> <http://www.w3.org/2000/01/rdf-schema#label> "{Article.title}" . 
            <http://vivo.school.edu/individual/{Article.n_num}> <http://vivoweb.org/ontology/core#hasPublicationVenue> <http://vivo.school.edu/individual/{Journal.n_num}> .
            <http://vivo.school.edu/individual/{Journal.n_num}> <http://vivoweb.org/ontology/core#publicationVenueFor> <http://vivo.school.edu/individual/{Article.n_num}> .
            <http://vivo.school.edu/individual/{Article.n_num}> <http://purl.org/ontology/bibo/volume> "{Article.volume}" .
            <http://vivo.school.edu/individual/{Article.n_num}> <http://purl.org/ontology/bibo/issue> "{Article.issue}" .
            <http://vivo.school.edu/individual/{Article.n_num}> <http://purl.org/ontology/bibo/pageStart> "{Article.start_page}" .
            <http://vivo.school.edu/individual/{Article.n_num}> <http://purl.org/ontology/bibo/pageEnd> "{Article.end_page}" .
        }}
    }}
    """.format(Article=article, Relationship=relationship_id, Author=author, Journal = journal)

    # send data to vivo
    print("Adding article with pre-existing author.")
    response = connection.run_update(q)
    return response