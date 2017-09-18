from jinja2 import Environment

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
    relationship_id = connection.gen_n()
    params['Relationship'] = relationship_id

    year_id = None
    if params['Article'].publication_year:
        year_id = connection.gen_n()
        params['Article'].final_check(year_id)
        params['Year'] = year_id

    #make sure none of the n numbers generated before inserting triples have repeating n numbers
    params['Article'].final_check(relationship_id)
    params['Article'].final_check(params['Journal'].n_num)

    # template data into q
    q = Environment().from_string("""\
        INSERT DATA {
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> 
            {
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle>  .
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://www.w3.org/2000/01/rdf-schema#label> "{{ Article.title }}" .
              
              {%- if Article.volume %}
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://purl.org/ontology/bibo/volume> "{{ Article.volume }}" .
              {%- endif -%}
              
              {%- if Article.issue %}
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://purl.org/ontology/bibo/issue> "{{ Article.issue }}" .
              {%- endif -%}
              
              {%- if Article.start_page %}
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://purl.org/ontology/bibo/pageStart> "{{ Article.start_page }}" .
              {%- endif -%}
              
              {%- if Article.end_page %}
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://purl.org/ontology/bibo/pageEnd> "{{ Article.end_page }}" .
              {%- endif -%}

              {%- if Article.publication_year %}
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://vivoweb.org/ontology/core#dateTimeValue> <http://vivo.school.edu/individual/{{ Year }}> .
                <http://vivo.school.edu/individual/{{ Year }}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#DateTimeValue> .
                <http://vivo.school.edu/individual/{{ Year }}> <http://vivoweb.org/ontology/core#dateTime> "{{ Article.publication_year }}-01-01T00:00:00" .
                <http://vivo.school.edu/individual/{{ Year }}> <http://vivoweb.org/ontology/core#dateTimePrecision> <http://vivoweb.org/ontology/core#yearPrecision> .
              {%- endif -%}
              
              {%- if Author.n_num %}
                <http://vivo.school.edu/individual/{{ Relationship }}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship>  .
                <http://vivo.school.edu/individual/{{ Relationship }}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{{ Article.n_num }}> .
                <http://vivo.school.edu/individual/{{ Relationship }}> <http://vivoweb.org/ontology/core#relates> <http://vivo.school.edu/individual/{{ Author.n_num }}> .
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://vivoweb.org/ontology/core#relatedBy> <http://vivo.school.edu/individual/{{ Relationship }}> .
              {%- endif -%}
              
              {%- if Journal.n_num %}
                <http://vivo.school.edu/individual/{{ Article.n_num }}> <http://vivoweb.org/ontology/core#hasPublicationVenue> <http://vivo.school.edu/individual/{{ Journal.n_num }}> .
                <http://vivo.school.edu/individual/{{ Journal.n_num }}> <http://vivoweb.org/ontology/core#publicationVenueFor> <http://vivo.school.edu/individual/{{ Article.n_num }}> .
              {%- endif %}
            }
        }
        """)

    # send data to vivo
    print('=' * 20 + "\nAdding article with pre-existing author\n" + '=' * 20)
    response = connection.run_update(q.render(**params))
    return response