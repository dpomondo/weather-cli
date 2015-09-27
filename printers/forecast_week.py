#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:   forecast_week.py
# -----------------------------------------------------------------------------

import sys
#  import math
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import utils.utilities as utils


def week_forecast(weat_db):
    color_flag = True   # this will eventually get set in a config file
    COLORS = utils.get_colors(color_flag=color_flag)
    width = utils.get_terminal_width()
    height = utils.get_terminal_height()
    num_days = len(weat_db)


def format_single_day(day, formatter):
    pass


def format_weeks(lis, box_width, box_height, formatter):
    """ takes a list of formatted lines, arranges them according to weekday
    """
    import datetime
    working = []
    start = datetime.datetime.fromtimestamp(utils.eat_keys(lis[0], ('date',
                                                                    'epoch'))) 
    if start > 0:
        tmp = []
        for j in range(box_height):
            tmp.append(' ' * box_width)
        for i in range(start):
            working.append(tmp)
    for day in lis:
        working.append(format_single_day(day, formatter))
