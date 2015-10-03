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
    #  color_flag = False   # this will eventually get set in a config file
    COLORS = utils.get_colors(color_flag=color_flag)
    width = utils.get_terminal_width()
    height = utils.get_terminal_height()
    #  num_days = len(weat_db)
    format_list, labels = temp_return_format()
    box_width = get_box_width(width - utils.max_len(labels))
    box_height = get_box_height(format_list, height)
    formatted_days = format_weeks(weat_db, box_width,
                                  box_height, format_list, COLORS)
    results = join_days(formatted_days, labels, box_width, box_height)
    return results


def join_days(formatted_days, labels, box_width, box_height):
    res = []
    label_width = utils.max_len(labels)
    while formatted_days:
        for index in range(box_height):
            res.append("{:<{wid}}{}".format(labels[index],
                       ''.join(d[index] for d in formatted_days[0:7]),
                       wid=label_width))
        formatted_days = formatted_days[7:]
    return res


def get_box_width(working_width):
    # the following is a cheat:
    return max(10, min(int(working_width/7), 20))


def get_box_height(formatter, height):
    return len(formatter)


def temp_return_format():
    """ temp function to return list to be parsed by make_formatter func
    """
    frmt = ['date', 'blank', 'temp_high_f', 'temp_low_f', 'blank']
    labels = ['', '', 'High', 'Low', '']
    return frmt, labels


def make_formatter(frmt_list, COLOR):
    """ returns a list of functions to be called in turn on a weather_db
    """
    import datetime as dt
    import printers.colorfuncs as cf

    def blank_line(day, _, box_width):
        return ' ' * box_width

    def date(day, _, box_width):
        temp = dt.datetime.fromtimestamp(int(utils.eat_keys(day, ('date',
                                                                  'epoch'))))
        working = temp.strftime('%A, %B %d')
        if len(working) * 1.5 > box_width:
            working = temp.strftime('%a, %b %d')
        return "{:^{wid}}".format(working[:box_width], wid=box_width)

    def high_temp(day, curr_day, box_width):
        temp = utils.eat_keys(day, ('high', 'fahrenheit'))
        base = utils.eat_keys(curr_day, ('high', 'fahrenheit'))
        #  return "{:^{wid}}".format("{}".format(temp), wid=box_width)
        return "{}{:^{wid}}{}".format(cf.bar_temp_color(temp, base, COLOR),
                                      "{} {}".format(temp, "F"),
                                      COLOR.clear,
                                      wid=box_width)

    def low_temp(day, curr_day, box_width):
        temp = utils.eat_keys(day, ('low', 'fahrenheit'))
        base = utils.eat_keys(curr_day, ('low', 'fahrenheit'))
        return "{}{:^{wid}}{}".format(cf.bar_temp_color(temp, base, COLOR),
                                      "{} {}".format(temp, "F"),
                                      COLOR.clear,
                                      wid=box_width)

    switch = {'date':           date,
              'blank':          blank_line,
              'temp_high_f':    high_temp,
              'temp_low_f':     low_temp}
    # make the function list...
    res = []
    for frmt in frmt_list:
        res.append(switch[frmt])
    return res


def format_single_day(day, curr_day, formatter, box_width):
    """ calls a list of function in formatter on the day object from a forcast
        returns a list of lines formatted to box_width length
    """
    res = []
    for func in formatter:
        res.append(func(day, curr_day, box_width))
    return res


def format_weeks(lis, box_width, box_height, format_list, COLOR):
    """ takes a list of formatted lines, arranges them according to weekday
    """
    import datetime
    working = []
    # here we'll have:
    assert isinstance(lis, list)
    assert isinstance(lis[0], dict)
    format_func = make_formatter(format_list, COLOR)
    start = int(datetime.datetime.fromtimestamp(
        int(utils.eat_keys(lis[0], ('date', 'epoch')))).weekday())
    if start > 0:
        tmp = []
        for j in range(box_height):
            tmp.append(' ' * box_width)
        for i in range(start):
            working.append(tmp)
    for day in lis:
        working.append(format_single_day(day, lis[0], format_func, box_width))
    return working
