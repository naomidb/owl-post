def run(connection, **kwargs):
    print("building request")
    # check for valid data
    relationship_id = connection.gen_n()
    article.final_check(relationship_id)

    print(article.label)
    print(article.n)
    print(author.n)
    print(relationship_id)

    # template data into q
    q = """
    INSERT DATA {{
       GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> 
       {{
            <http://vivo.school.edu/individual/{Article.n}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle>  .
            <http://vivo.school.edu/individual/{Relationship}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship>  .
            <http://vivo.school.edu/individual/{Relationship}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{Article.n}> .
            <http://vivo.school.edu/individual/{Relationship}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{Author.n}> .
            <http://vivo.school.edu/individual/{Article.n}> <http://vivoweb.org/ontology/core#relatedBy> <http://vivo.school.edu/individual/{Relationship}> .
            <http://vivo.school.edu/individual/{Article.n}> <http://www.w3.org/2000/01/rdf-schema#label> "{Article.label}" . 
        }}
    }}
    """.format(Article=article, Relationship=relationship_id, Author=author)

    # send data to vivo
    response = connection.run_query(q)
    return response