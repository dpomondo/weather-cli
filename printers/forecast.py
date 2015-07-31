#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#       file:       forecast.py
#     author:       dpomondo
#       deps:       called from getter.py
# -----------------------------------------------------------------------------

# import utilities
# from .utilities import *
import sys
import math
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import printers.utilities

# here we have the `magic` numbers, these will eventually be set in a
# config file
max_cols = 5
box_width = 20


def print_forecast(weat_db, frmt='lines'):
    if frmt == 'lines':
        lines_forecast(weat_db)
    elif frmt == 'grid':
        grid_forecast(weat_db)
    else:
        lines_forecast(weat_db)


def lines_forecast(weat_db):
    for day in weat_db:
        print("{}, {} {}:\thigh of {}, low of {}, {}".format(
            day['date']['weekday'],
            day['date']['monthname'],
            day['date']['day'],
            day['high']['fahrenheit'],
            day['low']['fahrenheit'],
            day['conditions']))


def grid_forecast(weat_db):
    # first, initialize all the vars
    num_days = len(weat_db)
    width = printers.utilities.get_terminal_width()
    height = printers.utilities.get_terminal_height()
    cols = min(max_cols, width//box_width)
    rows = math.ceil(num_days/cols)
    while rows * 10 > height:
        rows -= 1

    # now we build the thing
    pass


if __name__ == '__main__':
    print(printers.utilities.get_terminal_height())
    print(printers.utilities.get_terminal_width())
