#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       config.py
# -----------------------------------------------------------------------------

import json
import os
import time


def load_vars(config_file):
    with open(config_file, 'r') as infile:
        temp = json.load(infile)
    return temp


def day_file_name():
    home_dir = '/usr/self/weather'
    temp = os.path.join(home_dir,
                        'weather_data',
                        (time.strftime("%d%b%y") + "_weather"))
    return temp
