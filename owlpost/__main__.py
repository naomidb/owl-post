#!/usr/bin/env python

docstr = """
Usage:
    owlpost help
    owlpost errol (-a | -r) <config_file>
    owlpost hedwig (-q | -b) (-a | -r) <config_file>
    owlpost hermes (-a | -r) [-d] [-i] <config_file>
    owlpost pigwidgeon (-a | -r) [-x | -l] <config_file>
    owlpost owls <config_file>

Options:
     -a --api         Use VIVO api to upload data immediately
     -r --rdf         Produce rdf files with data
     -q --query       Use the WOS api to get new publication data (not functional)
     -b --bibtex      Get new publication data from bibtex file (path in config file)
     -d --database    Put api results into MySQL database
     -i --interact    Get query from user
     -x --xml         Use XML file to generate PMID list
     -l --list        Use file with just PMIDs listed
"""

from docopt import docopt

import ingests

def main(args):
    """
    Delegate to a tool in ingests.
    """
    if args.get('help'):
        print(docstr)
    elif args.get('errol'):
        ingests.errol.main(args)
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