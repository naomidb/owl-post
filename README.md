# owl-post
Send data back and forth from VIVO

The goal of owl-post is to allow users to interact with VIVO without having to learn the ontology, SPARQL, or anything about rdf. The list of available queries can be found in the queries directory.

### Before You Begin
Make sure to edit the example config file. If you do not update it, you will not be able to communicate with your VIVO.

## Config file
The config file requires different things depending on what tools you plan to use. As all ingests interact with VIVO, you will need the VIVO section filled. However, if you are only creating RDF files and not updating through the VIVO API, you do not need to fill in the update endpoint. 

```email: Username for account with API access
password: Password for the account

update_endpoint: Endpoint for update API
query_endpoint: Endpoint for query API

namespace: Namespace for your VIVO URIs
```

If you are intending to use the Web of Science API, you will need to fill in your credentials. These must be your username and password in the orientation below and then encoded in base 64.

```wos_credentials: '"Username:Password" encoded in base 64'```

You will also need some information on where to find and store things on your local machine. If you are using an input file (e.g. a bibtex file for the WOS ingest), you will need to put it after 'input_file'.

```input_file: 'data_in/your_file.bib'```

On the other hand, if you are using the grant ingest, errol, place the path to your input file after 'grant_file'.

```grant_file: /data_in/grant_file.csv```

You will need to provide a location for log files to be stored, however this folder does not have to exist before running. The directory structure will be created if it does not already exist.

```folder_for_logs: 'path/to/folder/logs/'```

If you have filters, list the filter folder in the config. The filters themselves have required names. The general filter, with swaps that are to be used for every name, should be called `general_filter.yaml`. The journal filter should be `journal_filter.yaml` and the publisher filter should be `publisher_filter.yaml`.

```filter_folder: 'path/to/folder/filters/'```

If you are storing the new information in a database, you must provide the database information.

```database: 'database_name'
database_port: 'database_port'
database_user: 'database_username'
database_pw: 'database_password'```


## Vivo Utils
Vivo Utils contains a collection of tools for producing queries, processing data, and interacting with VIVO.
The connections directory contains tools for creating connections to various APIs.
The handlers directory contains tools for handling the data from a particular source and parsing it as needed.
The queries directory contains pre-written query templates that can be used by other tools to create queries for getting or sending data through the VIVO API.
The vdos directory contains objects that represent Things in VIVO (e.g. People, Articles, etc.). These are used to gather data to fill in the queries. The VDOs for any particular query can be found in its `get_params` function.

## Owl Post

### owls
```python owls.py my/path/to/config/file```

owls is the command line version of manually adding or querying data to or from Vivo through the web interface. Simply run the program, and then select the query you would like by number from the list. Then follow the instructions (make sure to leave inputs blank for information you do not know). 

### hedwig
```python hedwig.py my/path/to/config/file```

hedwig takes bibtex files from `webofknowledge.com/wos` and converts them into triples which it then uploads. Search the webofknowledge site with your desired query and save the results as a bibtex file (optionally to the data_in folder). Then update the config file with the bibtex file location.

### pigwidgeon
```python pigwidgeon.py my/path/to/config/file```

pigwidgeon interacts with the pubmed API and adds publications to an author it will ask you to specify via the command line. pigwidgeon produces rdf files which can be uploaded to VIVO through VIVO's online interface.

### hermes
```python hermes.py -r my/path/to/config/file```

hermes will search pubmed for all publications based on a affliation and date (soon to be customizable) and upload them into VIVO. It parses all the journals, authors, publishers, and relationships. Then it checks and validates authors and journals for n-number in VIVO. Finally it puts it all together and uploads them into VIVO.

### errol