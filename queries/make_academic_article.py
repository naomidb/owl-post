from jinja2 import Environment

from author import Author
from article import Article
from journal import Journal

def get_params(connection):
    author = Author(connection)
    article = Article(connection)
    journal = Journal(connection)
    params = {'Author': author, 'Article': article, 'Journal': journal}
    return params


def run(connection, **params):
    params['Article'].create_n()
    relationship_id = connection.gen_n()
    params['Relationship'] = relationship_id
    params['Upload_url'] = connection.vivo_url

    year_id = None
    if params['Article'].publication_year:
        year_id = connection.gen_n()
        params['Article'].final_check(year_id)
        params['Year'] = year_id

    #make sure none of the n numbers generated before inserting triples have repeating n numbers
    params['Article'].final_check(relationship_id)
    params['Article'].final_check(params['Journal'].n_number)

    # template data into q
    q = Environment().from_string("""\
        INSERT DATA {
            GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2> 
            {
                <{{Upload_url}}{{ Article.n_number }}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/AcademicArticle>  .
                <{{Upload_url}}{{ Article.n_number }}> <http://www.w3.org/2000/01/rdf-schema#label> "{{ Article.name }}" .
              
              {%- if Article.volume %}
                <{{Upload_url}}{{ Article.n_number }}> <http://purl.org/ontology/bibo/volume> "{{ Article.volume }}" .
              {%- endif -%}
              
              {%- if Article.issue %}
                <{{Upload_url}}{{ Article.n_number }}> <http://purl.org/ontology/bibo/issue> "{{ Article.issue }}" .
              {%- endif -%}
              
              {%- if Article.start_page %}
                <{{Upload_url}}{{ Article.n_number }}> <http://purl.org/ontology/bibo/pageStart> "{{ Article.start_page }}" .
              {%- endif -%}
              
              {%- if Article.end_page %}
                <{{Upload_url}}{{ Article.n_number }}> <http://purl.org/ontology/bibo/pageEnd> "{{ Article.end_page }}" .
              {%- endif -%}

              {%- if Article.publication_year %}
                <{{Upload_url}}{{ Article.n_number }}> <http://vivoweb.org/ontology/core#dateTimeValue> <{{Upload_url}}{{ Year }}> .
                <{{Upload_url}}{{ Year }}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#DateTimeValue> .
                <{{Upload_url}}{{ Year }}> <http://vivoweb.org/ontology/core#dateTime> "{{ Article.publication_year }}-01-01T00:00:00" .
                <{{Upload_url}}{{ Year }}> <http://vivoweb.org/ontology/core#dateTimePrecision> <http://vivoweb.org/ontology/core#yearPrecision> .
              {%- endif -%}

              {%- if Article.doi %}
                <{{Upload_url}}{{Article.n_number}}> <http://purl.org/ontology/bibo/doi> "{{ Article.doi }}" .
              {%- endif -%}

              {%- if Article.pubmed_id %}
                <{{Upload_url}}{{Article.n_number}}> <http://purl.org/ontology/bibo/pmid> "{{ Article.pubmed_id }}" .
              {%- endif -%}
              
              {%- if Author.n_number %}
                <{{Upload_url}}{{ Relationship }}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Authorship>  .
                <{{Upload_url}}{{ Relationship }}> <http://vivoweb.org/ontology/core#relates> <{{Upload_url}}{{ Article.n_number }}> .
                <{{Upload_url}}{{ Relationship }}> <http://vivoweb.org/ontology/core#relates> <{{Upload_url}}{{ Author.n_number }}> .
                <{{Upload_url}}{{ Article.n_number }}> <http://vivoweb.org/ontology/core#relatedBy> <{{Upload_url}}{{ Relationship }}> .
              {%- endif -%}
              
              {%- if Journal.n_number %}
                <{{Upload_url}}{{ Article.n_number }}> <http://vivoweb.org/ontology/core#hasPublicationVenue> <{{Upload_url}}{{ Journal.n_number }}> .
                <{{Upload_url}}{{ Journal.n_number }}> <http://vivoweb.org/ontology/core#publicationVenueFor> <{{Upload_url}}{{ Article.n_number }}> .
              {%- endif %}
            }
        }
        """)

    # send data to vivo
    print('=' * 20 + "\nAdding article with pre-existing author\n" + '=' * 20)
    response = connection.run_update(q.render(**params))
    return response