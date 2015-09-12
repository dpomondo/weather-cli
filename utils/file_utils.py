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
    import updater
    keys = updater.list_keys(weat_db, verbose=False)
    return keys


def main():
    fils = list_dir()
    for f in fils:
        try:
            #  print(f)
            z = get_keys(f)
        except:
            z = []
        print("{}:\t{}".format(f, len(z)))


if __name__ == '__main__':
    main()
