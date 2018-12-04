from docopt import docopt
import os
import datetime
import pprint
import yaml

from vivo_utils import catalog
from vivo_utils import queries
from vivo_utils import vivo_log
from vivo_utils.connections import Connection
from vivo_utils.triple_handler import TripleHandler
from vivo_utils.update_log import UpdateLog
from vivo_utils import input_matcher

CONFIG_PATH = '<config_file>'
_api = '--api'
_rdf = '--rdf'


def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except Exception as e:
        print("Error: Check config file")
        print(e)
        exit()
    return config

def prepare_query(connection, added_journals, added_authors, tripler, ulog, db_name):
    template_choice = get_template_type()
    print(template_choice)

    template_mod = getattr(queries, template_choice)
    params = template_mod.get_params(connection)
    template_type = template_mod.return_type()

    for key, val in params.items():
        fill_details(connection, key, val, template_choice, added_journals,
                     added_authors, tripler, ulog, db_name)

    if template_type == 'update':
        response = tripler.update(template_mod, **params)
    else:
        response = tripler.run_query(template_mod, **params)

    pprint.pprint(response)

def get_template_type():
    available_queries = catalog.list_queries()
    template_options = {}

    for c, query in enumerate(available_queries, 1):
        template_options[c] = query

    menu_needed = 'y'
    menu_needed = input("Print query menu? (y/n) ")
    if menu_needed.lower() == 'y':
        for key, val in template_options.items():
            print(str(key) + ': ' + val + '\n')

    choice = input("Enter number of query or 'c' to cancel and exit program: ")
    if choice.lower() == 'c':
        raise Exception("User initiated exit")
    else:
        index = int(choice)
    return template_options.get(index)

def fill_details(connection, key, item, task, added_journals, added_authors, tripler, ulog, db_name):
    print('*' * 20 + '\n' * 2 + "Working on " + key + '\n' * 2 + '*' * 20)
    try:
        sub_task = "make_" + item.type
    except TypeError:
        sub_task = None  # A Thing will have a blank type

    print("Fill in the values for the following (if you do not have a value, leave blank):")
    # Check if user knows n number
    obj_n = input("N number: ")
    if obj_n:
        item.n_number = obj_n
        # TODO: add label confirmation
    elif key == 'Thing':
        print("You must have an N number")
    else:
        # Ask for label
        if key == 'Author':
            for alias in item.name_details:
                item_info = input(str(alias) + ': ')
                setattr(item, alias, item_info)
            item.combine_name()
        else:
            obj_name = input(key + ' name/title: ')
            item.name = obj_name.replace('"', '\\"')

        # Check if label already exists
        if item.category == 'person':
            matcher = 'person'
        elif item.category == 'publication':
            matcher = 'publication'
        elif item.type == 'journal':
            matcher = 'journal'
        else:
            matcher = None

        if matcher:
            match = local_match_input(item.name, matcher, added_authors, added_journals, db_name)
        else:
            match = vivo_match_input(connection, item.name, item.type, tripler)

        if not match:
            if sub_task != task:
                # If this entity is not the original query, make entity
                create_obj = input("This " + item.type + " is not in the database. Would you like to add it? (y/n) ")
                if create_obj.lower() == 'y':
                    try:
                        for feature in item.details:
                            item_info = input(str(feature) + ': ')
                            setattr(item, feature, item_info)
                        update_path = getattr(queries, sub_task)
                        sub_params = update_path.get_params(connection)
                        sub_params[key] = item

                        response = tripler.update(update_path, **sub_params)
                        print(response)
                    except Exception as e:
                        print('Owl Post failed to create ' + item.type + 'due to the error below.' +
                                'Please go to your vivo site and make it manually.')
                        print(e)
                        print('If you have manually made the ' + item.type + ' write it here.' +
                                'Otherwise, click enter without writing anything.')
                        match = input('N number: ')
            else:
                for feature in item.details:
                    item_info = input(str(feature) + ': ')
                    setattr(item, feature, item_info)
        if match:
            item.n_number = match
            print("The n number for this " + item.type + " is " + item.n_number)
    return


def local_match_input(label, matcher, added_authors, added_journals, db_name):
    ''' Find match by checking temporary database '''
    if matcher == 'person':
        matches = input_matcher.author_match(label, db_name, added_authors)
    elif matcher == 'publication':
        matches = input_matcher.pub_matching(label, db_name)
    elif matcher == 'journal':
        matches = input_matcher.journal_matching(label, db_name, added_journals)

    index = -1
    if matches:
        count = 1
        for option in matches:
            print(str(count) + ': ' + option[1] + '(' + option[0] + ')\n')
            count += 1

        index  = int(input("Do any of these match your input? (if none, write -1): "))

    if not index == -1:
        match = matches[index - 1][0]
    else:
        match = None

    return match

def vivo_match_input(connection, label, obj_type, tripler):
    ''' Find match by querying to VIVO '''
    details = queries.find_n_for_label.get_params(connection)
    details['Thing'].extra = label
    details['Thing'].type = obj_type

    print(category)

    # matches = queries.find_n_for_label.run(connection, **details)
    matches = tripler.run_query(queries.find_n_for_label, **details)

    choices = {}
    count = 1
    for key, val in matches.items():
        choices[count] = (key, val)
        count += 1

    index = -1
    if choices:
        for key, val in choices.items():
            number, label = val
            print(str(key) + ': ' + label + ' (' + number +')\n')

        index = int(input("Do any of these match your input? (if none, write -1): "))

    if not index == -1:
        nnum, label = choices.get(index)
        match = nnum
    else:
        match = None

    return match

def main(args):
    config = get_config(args[CONFIG_PATH])
    email = config.get('email')
    password = config.get('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    namespace = config.get('namespace')
    filter_folder = config.get('filter_folder')

    db_name = '/tmp/vivo_temp_storage.db'

    connection = Connection(namespace, email, password, update_endpoint, query_endpoint)
    vivo_log.update_db(connection, db_name, ['authors', 'journals', 'publications'])

    try:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y_%m_%d")
        full_path = os.path.join(config.get('folder_for_logs'),
            now.strftime("%Y")+ '/' + now.strftime("%m") + '/' + now.strftime("%d"))
        try:
            os.makedirs(full_path)
        except FileExistsError:
            pass

        output_file = os.path.join(full_path, (timestamp + '_owls_output_file.txt'))
        upload_file = os.path.join(full_path, (timestamp + '_owls_upload_log.txt'))

        meta = {'source': 'Owls', 'harvest_date': now.strftime("%Y-%m-%d")}
        tripler = TripleHandler(args[_api], connection, meta, output_file)
        ulog = UpdateLog()

        added_journals = {}
        added_authors = {}

        cont = 'y'
        while cont.lower() == 'y':
            prepare_query(connection, added_journals, added_authors, tripler, ulog, db_name)
            cont = input("Would you like to continue? (y/n) ")

        # Write rdf file if applicable
        os.remove(db_name)
        if args[_rdf]:
            rdf_filepath = os.path.join(full_path, (timestamp + '_owls_upload.rdf'))
            tripler.print_rdf(rdf_filepath)


    except Exception:
        # Write rdf file if applicable
        os.remove(db_name)
        if args[_rdf]:
            rdf_filepath = os.path.join(full_path, (timestamp + '_owls_upload.rdf'))
            tripler.print_rdf(rdf_filepath)
        import traceback
        exit(traceback.format_exc())
