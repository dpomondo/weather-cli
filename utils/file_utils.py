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


def parse_databse(db_files, key_list, filter_func=lambda x: True):
    """ returns a dictionary consisting of data parsed from a list of files.

        key_list:   a tuple of strings, suitable for eat_keys func
    """
    import utils.utilities as utils
    res = {}
    for k in key_list:
        res[k] = []
    for fil in db_files:
        keys = list(filter(lambda x: x != 'current_response',
                           get_keys(fil)))
        for ky in keys:
            if filter_func(fil[ky]) is True:
                for k in key_list:
                    res[k].append(utils.eat_keys(fil[ky], k))
    return res


def main():
    fils = list_dir()
    total = 0
    for f in fils:
        try:
            #  print(f)
            z = get_keys(f)
            total += len(z)
        except:
            z = []
        print("{}:\t{}".format(f, len(z)))
    print("{} total files with {} total keys".format(len(fils), total))

if __name__ == '__main__':
    main()
