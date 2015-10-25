#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:       config.py
# -----------------------------------------------------------------------------

import json
import os
import time
import datetime as dt
home_dir = '/usr/self/weather'
data_dir = 'weather_data'
log_dir = 'logs'


def load_vars(config_file):
    with open(config_file, 'r') as infile:
        temp = json.load(infile)
    return temp


def day_file_name(time=dt.date.today()):
    return os.path.join(home_dir,
                        data_dir,
                        #  (time.strftime("%d%b%y") + "_weather"))
                        (time.strftime("%d%b%y") + "_weather"))
    #  return temp


def log_file_name():
    return os.path.join(home_dir, log_dir, (time.strftime("%d%b%y") + "_log"))


def current_file_name():
    return day_file_name() + ".json"


def config_file_name():
    return os.path.join(home_dir, 'config', 'jwunderground.json')


def parse_config():
    class configurator:
        pass
    res = configurator()
    config_list = {"print_hourly": "cols"}
    for key in config_list:
        setattr(res, key, config_list[key])
    return res


def key_formatter(dic):
    key_color = '\033[38;5;214m'
    val_color = '\033[38;5;056m'
    end_color = '\033[0m'
    results = []
    new_len = 1
    for k in dic:
        if 1 + len(k) > new_len:
            new_len = len(k) + 1
    for key in sorted(dic.keys()):
        if isinstance(dic[key], dict):
            # remember kids: recursion is cool
            temp = key_formatter(dic[key])
            results.append("{}{}:{:<{width}}{}".format(key_color,
                                                       key,
                                                       " ",
                                                       end_color,
                                                       width=(new_len-len(key))
                                                       ))
            if len(temp) > 0:
                results[-1] += temp[0]
                for t in temp[1:]:
                    results.append((" " + " " * new_len) + t)
        else:
            results.append("{}{}:{:<{width}}{}{}{}".format(key_color,
                                                           key,
                                                           " ",
                                                           val_color,
                                                           dic[key],
                                                           end_color,
                                                           width=new_len-len(
                                                               key)))
    return results


def main():
    print("`home_dir` var is:\t{}".format(home_dir))
    print("day file name is:\t{}".format(day_file_name()))
    print("config file name:\t{}".format(config_file_name()))
    print("current file name is:\t{}".format(current_file_name()))
    temp = load_vars(config_file_name())
    print("Current config file contents:")
    z = key_formatter(temp)
    for lin in z:
        print(lin)
    # print("did we get this far?")

if __name__ == '__main__':
    main()
