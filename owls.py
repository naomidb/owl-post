import os
import os.path
import yaml

import APIsmith

def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config

def get_type():
    dir = os.getcwd()
    direc = os.path.join(dir, 'queries')

    x = {}
    count = 1
    for file in os.listdir(direc):
        x[count] = file
        count += 1

    for key, val in x.items():
        print(str(key) + ': ' + val + '\n')

    index = input("Write the number of your desired query type: ")
    return x.get(index)

def get_params(query_type):
    if query_type.startswith("make_pub"):
        if query_type.startswith("make_pub_new_author"):
            #do stuff
            #make author -> new_pub_old_author ?
        else:
            print("Fill in values for the following prompts. If you do not have a value for one of them, you may leave it blank.")
            author_id = input("N number of author (include n): ")
            label = input("Title: ")
            page_start = input("Starting page: ")
            page_end = input("Ending page: ")
            params = {'author_id': author_id, 'pub_title': '', 'page_start': '', 'page_end': ''}
            return params
    elif query_type.startswith("make_author"):
        #dostuff
    #etc.

def main(argv1):
    config_path = argv1
    config = get_config(config_path)

    query_type = get_type()
    params = get_params(query_type)

    #author_id = input("Enter the n number of the author (including the n): ")
    #identifier = {'number': author_id}

    #article_label = input("What is the title of the article? (please use quotation marks) ")

    APIsmith.main(config, params)

    cont = input("Would you like to add another publication? (y/n) ")
    if cont == 'y':
        APIsmith.main(config, identifier)

    new_author = input("Would you like to work on a new author? (y/n) ")
    if new_author == 'y':
        main(config_path)

if __name__ == '__main__':
    main(sys.argv[1:])