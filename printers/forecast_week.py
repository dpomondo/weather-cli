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
    #  color_flag = True   # this will eventually get set in a config file
    #  COLORS = utils.get_colors(color_flag=color_flag)
    width = utils.get_terminal_width()
    height = utils.get_terminal_height()
    #  num_days = len(weat_db)
    box_width = get_box_width(width)
    box_height = get_box_height(temp_return_format, height)
    formatted_days = format_weeks(weat_db, box_width,
                                  box_height, get_formatter)
    results = join_days(formatted_days, box_width, box_height)
    return results


def join_days(formatted_days, box_width, box_height):
    res = []
    while formatted_days:
        for index in range(box_height):
            res.append(''.join(d[index] for d in formatted_days[0:7]))
        formatted_days = formatted_days[7:]
    return res


def get_box_width(width):
    # the following is a cheat:
    return 15


def get_box_height(formatter, height):
    return len(formatter())


def temp_return_format():
    """ temp function to return list to be parsed by get_formatter func
    """
    return ['blank', 'temp_high_f', 'blank']


def get_formatter(frmt_list):
    """ returns a list of functions to be called in turn on a weather_db
    """
    #  import printers.colorfuncs as cf
    def blank_line(day, box_width):
        return ' ' * box_width

    def high_temp(day, box_width):
        temp = utils.eat_keys(day, ('high', 'fahrenheit'))
        return "{:^{wid}}".format(temp, wid=box_width)

    # TODO: dictionary matching format keys to functions
    switch = {'blank':          blank_line,
              'temp_high_f':    high_temp}
    # make the function list...
    res = []
    for frmt in frmt_list:
        res.append(switch[frmt])
    return res


def format_single_day(day, formatter, box_width):
    """ calls a list of function in formatter on the day object from a forcast
        returns a list of lines formatted to box_width length
    """
    res = []
    for func in formatter:
        res.append(func(day, box_width))
    return res


def format_weeks(lis, box_width, box_height, formatter):
    """ takes a list of formatted lines, arranges them according to weekday
    """
    import datetime
    working = []
    # here we'll have:
    assert isinstance(lis, list)
    assert isinstance(lis[0], dict)
    format_func = formatter(temp_return_format())
    start = int(datetime.datetime.fromtimestamp(
        int(utils.eat_keys(lis[0], ('date', 'epoch')))).weekday())
    if start > 0:
        tmp = []
        for j in range(box_height):
            tmp.append(' ' * box_width)
        for i in range(start):
            working.append(tmp)
    for day in lis:
        working.append(format_single_day(day, format_func, box_width))
    return working
