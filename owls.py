import os
import os.path
import sys
import yaml

from owlery import Connection
import queries

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

def get_template_type():
    dir = os.getcwd()
    direc = os.path.join(dir, 'queries')

    template_options = {}
    count = 1
    for file in os.listdir(direc):
        if file.startswith('__init__') or file.endswith('.pyc'):
            pass
        else:
            template_options[count] = file
            count += 1

    for key, val in template_options.items():
        print(str(key) + ': ' + val + '\n')

    index = input("Write the number of your desired template type: ")
    return template_options.get(index)

def fill_details(key, item, connection):
    """
    Given an item which is an instance of a VivoDomainObject, calls get_details and iterates through the list, prompting the user for the literal values.
    """

    print('*' * 20 + '\n' * 2 + "Working on " + key + '\n' * 2 + '*' * 20)
    print("Fill in the values for the following (if you do not have a value, leave it blank):")
    #For journals, check user input against pre-existing journals
    if item.type == 'journal':
        #fill this in
        pass

    details = item.get_details()
    for feature in details:
        my_input = raw_input(str(feature) + ": ")
        setattr(item, feature, my_input)


    """if item.type == 'journal':
        params = (1,2)
        journal_list = get_journals.run(connection, *params)
    else:
        print("Fill in the values for the following (if you do not have a value, leave it blank):")
        details = item.get_details()
        for feature in details:
            my_input = raw_input(str(feature) + ": ")
            setattr(item, feature, my_input)"""

def match_input(existing_options):
    choices = {}
    count = 1
    for key, val in existing_options.items():
        choices[count] = key
    for key, val in choices.items():
        print(str(key) + ': ' + val + '\n')

    index = input("Do any of these match your" + journal + "? (if none, write 'n'): ")
    if not index == 'n':
        #fill this in
        pass


def main(argv1):
    config_path = argv1
    config = get_config(config_path)

    email = config.get('email')
    password = config.get ('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')
    check_url = config.get('checking_url')

    connection = Connection(vivo_url, check_url, email, password, update_endpoint, query_endpoint)

    template_type = get_template_type()

    head, sep, tail = template_type.partition('.')
    template_choice = head
    print(template_choice)

    template_mod = getattr(queries, template_choice)
    params = template_mod.get_params(connection)

    for key, val in params.items():
        fill_details(key, val, connection)
        print(type(val))

    '''for item in params:
        details = item.get_details()
        for feature in details:
            trait = getattr(item, feature)'''

    response = template_mod.run(connection, **params)
    print(response)

if __name__ == '__main__':
    main(sys.argv[1])