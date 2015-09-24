#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       file_utils.py
# -----------------------------------------------------------------------------

import sys
import os
home_dir = '/usr/self/weather/'
if home_dir not in sys.path:
    sys.path.append(home_dir)
import config.loaders


def list_dir(verbose=True):
    data_dir = config.loaders.data_dir
    if verbose:
        print("Data dir is: " + data_dir)
    files = os.listdir(data_dir)
    res = list(os.path.abspath(os.path.join(os.getcwd(), data_dir, fil)) for
               fil in files if not fil.endswith('.json'))
    attribute = 'st_birthtime'
    if verbose:
        print("sorting by '{}' attribute".format(attribute))
    return sorted(res, key=lambda fil: getattr(os.stat(fil), attribute))


def get_keys(weat_db):
    """ return a list of keys in a shelve file
    """
    import updater
    keys = updater.list_keys(weat_db, verbose=False)
    return keys


def parse_database(db_files, key_list, filter_func=lambda x: True):
    """ returns a dictionary consisting of data parsed from a list of files.

        key_list:   a tuple of strings, suitable for eat_keys func
    """
    import shelve
    import utils.utilities as utils
    res = {}
    for k in key_list:
        res[k] = []
    for fil in db_files:
        #  print("Opening {}...".format(fil))
        tar = shelve.open(fil)
        keys = list(z for z in list(tar.keys()) if z != 'current_response')
        for ky in keys:
            #  if filter_func(tar[ky]) is True:
            for k in key_list:
                res[k].append(utils.eat_keys(tar[ky], k))
        tar.close()
    return res


def main():
    # test list_dir and get_keys
    fils = list_dir()
    total = 0
    for f in fils:
        try:
            pass
            #  print(f)
            #  z = get_keys(f)
            #  total += len(z)
        except:
            z = []
        #  print("{}:\t{}".format(f, len(z)))
    #  print("{} total files with {} total keys".format(len(fils), total))
    # test parse_database
    import random
    import pprint
    import shelve
    target = random.sample(fils, 4)
    #  test_db = shelve.open(target)
    print('-' * 80)
    print("Testing file '{}'".format(target))
    target_keys = []
    target_keys.append(('current_observation', 'temp_f'))
    target_keys.append(('current_observation', 'wind_gust_mph'))
    res = parse_database(target, target_keys)
    for key in res:
        print('-' * 40 + '\n' + str(key))
        pprint.pprint(res[key])


if __name__ == '__main__':
    main()
