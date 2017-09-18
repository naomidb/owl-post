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
    if key == 'Journal':
        journal = item

        journal.title = raw_input("title: ")
        #if user did not leave title blank, check if title is in list of current journals
        if journal.title:
            deets = {}
            current_journals = queries.get_journals.run(connection, **deets)

            match = match_input(journal.title, current_journals)
            if match == 'none':
                journal.create_n()
                params = {'New Journal': journal}
                queries.make_journal.run(connection, **params)

            else:
                journal.n_num = match
                print("The n number for this journal is " + journal.n_num)

    elif key == 'Author':
        author = item

        auth_num = raw_input("N number (if you do not know the n number, leave this blank): ")
        #If user does not know author n number, search for author
        if auth_num:
            author.n_num = auth_num
        else:
            auth_name = raw_input("Author name: ")
            #add author search here

    else:
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

def match_input(title, existing_options):
    choices = {}
    count = 1
    for key, val in existing_options.items():
        if title.lower() in key.lower():
            choices[count] = key
            count += 1

    index = -1
    if choices:
        for key, val in choices.items():
            print(str(key) + ': ' + val + '\n')

        index = input("Do any of these match your input? (if none, write -1): ")
    if not index == -1:
        title = choices.get(index)
        match = existing_options.get(title)
    else:
        match = 'none'

    return match

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

    response = template_mod.run(connection, **params)
    print(response)

if __name__ == '__main__':
    main(sys.argv[1])