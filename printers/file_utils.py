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


def list_dir():
    data_dir = config.loaders.data_dir
    files = os.listdir(data_dir)
    res = list(fil for fil in files if not fil.endswith('.json'))
    return res


def get_keys(weat_db):
    import updater
    keys = updater.list_keys(weat_db, verbose=False)
    return keys


def main():
    fils = list_dir()
    for f in fils:
        try:
            z = get_keys(f)
        except:
            z = []
        print("{}:\t{}".format(f, len(z)))


if __name__ == '__main__':
    main()
