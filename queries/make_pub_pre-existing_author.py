def run(connection, author, article):
    # check for valid data
    relationship_id = connection.get_n()
    article_id = article.final_check(relationship_id)

    # template data into q
    q = """
        INSERT DATA {
           GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> 
           {
                <http://vivo.school.edu/individual/{Article}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle>  .
                <http://vivo.school.edu/individual/{Relationship}}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship>  .
                <http://vivo.school.edu/individual/{Relationship}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{Article}> .
                <http://vivo.school.edu/individual/{Relationship}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{Author}> .
                <http://vivo.school.edu/individual/{Article}> <http://vivoweb.org/ontology/core#relatedBy> <http://vivo.school.edu/individual/{Relationship}> .
                <http://vivo.school.edu/individual/{Article}> <http://www.w3.org/2000/01/rdf-schema#label> "{Article.label}" . 
            }
        }
    """.format(Article=article_id, Relationship=relationship_id, Author=author.n)

    # send data to vivo
    pass









