#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:   summary_utils.py
# -----------------------------------------------------------------------------

import sys
import os
home_dir = '/usr/self/weather/'
if home_dir not in sys.path:
    sys.path.append(home_dir)
import utils.utilities as utils
import utils.file_utils as file_utils

def vector_maker(file_list, keys):
    res = []
    for fil in file_list:
        pass
