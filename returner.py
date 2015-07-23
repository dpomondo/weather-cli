#! /usr/local/bin/python3
# coding=utf-8

import json
import sys
import os
import time

time_out = 600
home_dir = '/usr/self/weather/'
shelve_file = home_dir + time.strftime("%d%b%y") + "_weather"
today_current = shelve_file + ".json"


def call_getter():
    if '/usr/self/bin' not in sys.path:
        sys.path.append('/usr/self/bin')
    import shelve
    import getter
    # need to move this `shelve.open` call to the update function...
    weather_db = shelve.open(shelve_file)
    getter.update(weather_db, check_time=False)
    weather_db.close()


def open_current_file():
    with open(today_current, "r") as infile:
        temp = json.load(infile)
    return temp


def get_current_time(temp):
    return int(temp['current_observation']['observation_epoch'])


def temp_current_get(temp):
    return temp['current_observation']['temp_f']


def main():
    if not os.path.isfile(today_current):
        call_getter()
    current = open_current_file()
    ob_ep = get_current_time(current)
    if ob_ep + time_out < time.time():
        call_getter()
    temperature = temp_current_get(current)
    return "Current Temp: {}".format(temperature)


if __name__ == "__main__":
    out = main()
    sys.stdout.write(out)
