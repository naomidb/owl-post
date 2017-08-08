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

def main(argv1):
    config_path = argv1
    config = get_config(config_path)

    author_id = input("Enter the n number of the author (including the n): ")
    identifier = {'number': author_id}

    APIsmith.main(config, identifier)

    cont = input("Would you like to add another publication? (y/n) ")
    if cont == 'y':
        APIsmith.main(config, identifier)

    new_author = input("Would you like to work on a new author? (y/n) ")
    if new_author == 'y':
        main(config_path)

if __name__ == '__main__':
    main(sys.argv[1:])