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
database_pw: 'database_password'
```

## Vivo Utils
Vivo Utils contains a collection of tools for producing queries, processing data, and interacting with VIVO.
The connections directory contains tools for creating connections to various APIs.
The handlers directory contains tools for handling the data from a particular source and parsing it as needed.
The queries directory contains pre-written query templates that can be used by other tools to create queries for getting or sending data through the VIVO API.
The vdos directory contains objects that represent Things in VIVO (e.g. People, Articles, etc.). These are used to gather data to fill in the queries. The VDOs for any particular query can be found in its `get_params` function.


## Owl Post

### owls
```python owlpost owls <config_file>```

A command line tool for adding/querying data to/from VIVO. Run the program and select from a pre-designed selection of queries. Follow the instructions and make sure to leave the input blank for information you do not know.

### hedwig
```python owlpost hedwig (-a | -r) (-q | -b) <config_file>```

Use a bibtex file from Web of Science and convert it into triples to be uploaded to VIVO. Information can be sent to VIVO via the API or an rdf file can be produced to be manually uploaded. Edit the `input_file` in the config with the bibtex file.

Use `-a` to upload data to VIVO via the VIVO API.
Use `-r` to produce an rdf file with data for VIVO.
Use `-q` to run a query through the WOS API. [Note: The ingest does not currently work with this option. Use a bibtex file.]
Use `-b` to get data from a bibtex file downloaded from WOS.

### hermes
```python owlpost hermes (-a | -r) [-d] [-i] <config_file>```

Use the PubMed API to pull data from PubMed and convert it into triples to be uploaded to VIVO. Information can be sent to VIVO via the API or an rdf file can be produced to be manually uploaded.

Use `-a` to upload data to VIVO via the VIVO API.
Use `-r` to produce an rdf file with data for VIVO.
Use `-d` to store the publications pulled in by the ingest in a separate, permanent database.
Use `-i` to manually enter a query instead of using the default one.

### pigwidgeon
```python owlpost pigwidgeon (-a | -r) [-x | -l] <config_file>```

Use the PubMed API to pull data from PubMed and convert it into triples to be uploaded to VIVO. You can search Pubmed with a query, or use the `-x` or `-l` flags to get the PubmedID list from a file. If you use `-x`, the file must be XML (which is the file type you will get by downloading a list from Pubmed). If you use the `-l` flag, the file should have each PubmedId on its own line.

Unlike Hermes, this tool asks for an individual Person in VIVO and adds all publications from a query to that person only. Information can be sent to VIVO via the API or an rdf file can be produced to be manually uploaded.

Use `-a` to upload data to VIVO via the VIVO API.
Use `-r` to produce an rdf file with data for VIVO.
Use `-x` to get the PubmedIDs from an xml file.
Use `-l` to get the PubmedIDs from a file with just the IDs listed.

### errol
```python errol (-a | -r) <config_file>```

Use `-a` to upload data to VIVO via the VIVO API.
Use `-r` to produce an rdf file with data for VIVO.