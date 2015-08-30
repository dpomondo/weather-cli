#! /usr/local/bin/python3
# coding=utf-8

import json
import sys
import os
import time

home_dir = '/usr/self/weather/'
if home_dir not in sys.path:
    sys.path.append(home_dir)
import config.loaders
# change allo these to function calls:


def call_getter():
    if '/usr/self/bin' not in sys.path:
        sys.path.append('/usr/self/bin')
    # import shelve
    import getter
    getter.update(check_time=False)
    # weather_db.close()


def open_current_file():
    with open(config.loaders.current_file_name(), "r") as infile:
        temp = json.load(infile)
    return temp


def get_current_time(temp):
    return int(temp['current_observation']['observation_epoch'])


def temp_current_get(temp):
    return temp['current_observation']['temp_f']


def main(time_out=600):
    if not os.path.isfile(config.loaders.current_file_name()):
        call_getter()
    current = open_current_file()
    ob_ep = get_current_time(current)
    if ob_ep + time_out < time.time():
        call_getter()
    # kill the following:
    # sys.stdout.write("{} {}".format(sys.argv[0], __name__))
    # return "{} {} {}".format(sys.argv[0], __name__, __name__)
    if __name__ == "__main__":
        # if we get called from the shell function:
        temperature = temp_current_get(current)
        return "Current Temp: {}".format(temperature)
    else:
        # if we get called from getter.py, return the whole current response:
        return current


if __name__ == "__main__":
    out = main()
    sys.stdout.write(out)
