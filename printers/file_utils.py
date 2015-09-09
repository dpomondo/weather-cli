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


def main():
    fils = list_dir()
    for f in fils:
        print(f)


if __name__ == '__main__':
    main()
