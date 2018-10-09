docstr = """
Usage:
    help
    hedwig (-q | -b) (-a | -r) <config_file>
    hermes (-a | -r) [-d] [-i] <config_file>
    pigwidgeon (-a | -r) <config_file>
    owls <config_file>

Options:
     -a --api         Use VIVO api to upload data immediately
     -r --rdf         Produce rdf files with data
     -q --query       Use the WOS api to get new publication data (not functional)
     -b --bibtex      Get new publication data from bibtex file (path in config file)
     -d --database    Put api results into MySQL database
     -i --interact    Get query from user
"""

from docopt import docopt

from owlpost import ingests

CONFIG_PATH = '<config_file>'
_query = '--query'
_bibtex = '--bibtex'
_api = '--api'
_rdf = '--rdf'
_db = '--database'
_interact = '--interact'

def main(args):
    """
    Delegate to a tool in ingests.
    """
    if args.get('help'):
        print(docstr)
    elif args.get('hedwig'):
        ingests.hedwig.main(args)
    elif args.get('hermes'):
        ingests.hermes.main(args)
    elif args.get('pigwidgeon'):
        ingests.pigwidgeon.main(args)
    elif args.get('owls'):
        ingests.owls.main(args)

def cli_run():
    """
    This is the entry point to the script when run from the command line with
    as specified in the setup.py
    """
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()