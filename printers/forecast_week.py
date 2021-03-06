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


def week_forecast(weat_db, width):
    color_flag = True   # this will eventually get set in a config file
    #  color_flag = False   # this will eventually get set in a config file
    COLORS = utils.get_colors(color_flag=color_flag)
    #  width = utils.get_terminal_width()
    height = utils.get_terminal_height()
    #  there has to be a more elegant way to do the following:
    format_tups = temp_return_format()
    format_list = list(x[0] for x in format_tups['body'])
    labels = []
    #  labels = list(x[1] for x in format_tups['body'])
    for lab in format_tups['body']:
        if lab[2] == 1:
            labels.append(lab[1])
        elif lab[2] > 1:
            temp = []
            temp.append(lab[1])
            for i in range(lab[2] - 1):
                temp.append('')
            labels.extend(temp)
        else:
            raise ValueError("formatter returned negative value")
    box_width = get_box_width(width - utils.max_len(labels))
    #  box_height = get_box_height(format_list, height)
    box_height = get_box_height(format_tups['body'], height)
    formatted_days = format_day_list(weat_db, box_width,
                                     box_height, format_list,
                                     COLORS)
    formatted_header = format_header(None, utils.max_len(labels), box_width,
                                     COLORS)
    results = join_days(formatted_days, formatted_header, labels, width,
                        box_width, box_height, COLORS)
    return results


def join_days(formatted_days, formatted_header, labels, width, box_width,
              box_height, COLORS):
    res = []
    label_width = utils.max_len(labels)
    total_width = label_width + (7 * box_width)
    #  assert width > total_width
    for lin in formatted_header:
        res.append("{:^{wid}}{}".format('', lin,
                                        wid=int(0.5 * (width - total_width))))
    while formatted_days:
        for index in range(box_height):
            temp = ''.join(d[index] for d in formatted_days[0:7])
            temp = "{:>{wid}}{}".format(labels[index], temp, wid=label_width)
            temp = "{:>{wid}}{}".format('', temp,
                                        wid=int(0.5 * (width - total_width)))
            res.append(temp)
        formatted_days = formatted_days[7:]
    return res


def get_box_width(width):
    # the following is a cheat:
    #  return 15
    return max(6, min(int(width/7), 18))


def get_box_height(formatter, height):
    #  return len(formatter)
    return sum(list(x[2] for x in formatter))


def temp_return_format():
    """ temp function to return dict to be parsed by make_formatter func
    """
    frmt = {'body':     [('dash', '', 1),
                         ('date', '', 1),
                         ('blank', '', 1),
                         ('temp_high_f', 'High', 1),
                         ('temp_low_f', 'Low', 1),
                         #  ('blank', '', 1),
                         ('precip', 'Precipitation', 1),
                         ('wind_sd', 'Wind (mph)', 1),
                         ('conditions', 'Conditions', 2)
                         #  ('blank', '', 1)
                        ]}
    return frmt


def make_formatter(frmt_list, COLOR):
    """ returns a list of functions to be called in turn on a weather_db
    """
    import datetime as dt
    import printers.colorfuncs as cf

    def dashed_line(day, _, box_width):
        return '-' * box_width

    def dashed_with_corners(day, _, box_width):
        return "{}{}{}".format('+', '-' * box_width - 2, '+')

    def blank_line(day, _, box_width):
        return ' ' * box_width

    def weekday(day, _, box_width):
        temp = dt.datetime.fromtimestamp(int(utils.eat_keys(day, ('date',
                                                                  'epoch'))))
        working = temp.weekday()
        if len(working) > box_width:
            working = working[:3]
        return "{:^{wid}}".format(working[:box_width], wid=box_width)

    def date(day, _, box_width):
        temp = dt.datetime.fromtimestamp(int(utils.eat_keys(day, ('date',
                                                                  'epoch'))))
        working = temp.strftime('%B %e')
        if len(working) * 1.5 > box_width:
            working = temp.strftime('%b %e')
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

    def precip(day, curr_day, box_width):
        qpf = utils.eat_keys(day, ('qpf_allday', 'in'))
        snow = utils.eat_keys(day, ('snow_allday', 'in'))
        return "{}{:^{wid}}{}".format(cf.inch_precip_color((qpf + snow),
                                                           None, COLOR),
                                      "{:.3} {}".format(qpf+snow, "in"),
                                      COLOR.clear,
                                      wid=box_width)

    def wind_speed_dir(day, curr_day, box_width):
        speed = utils.eat_keys(day, ('maxwind', 'mph'))
        direction = utils.eat_keys(day, ('maxwind', 'dir'))
        curr_speed = utils.eat_keys(curr_day, ('maxwind', 'mph'))
        if direction is not None:
            return "{}{:^{wid}}{}".format(cf.bar_temp_color(speed,
                                                            curr_speed,
                                                            COLOR),
                                          "{} {}".format(speed, direction),
                                          COLOR.clear,
                                          wid=box_width)
        else:
            return "{}{:^{wid}}{}".format(cf.bar_temp_color(speed,
                                                            curr_speed,
                                                            COLOR),
                                          speed,
                                          COLOR.clear,
                                          wid=box_width)

    def conditions(day, curr_day, box_width):
        conds = utils.eat_keys(day, ('conditions',))
        if len(conds) < box_width:
            first = "{}{:^{wid}}{}".format(COLOR.cond, conds, COLOR.clear,
                                           wid=box_width)
            second = ' ' * box_width
            #  return [first, second]
        else:
            tmp = conds.split(' ')
            first, second = '', ''
            while len(first) + len(tmp[0]) < box_width:
                first = first + ' ' + tmp[0]
                tmp = tmp[1:]
            first = "{}{:^{wid}}{}".format(COLOR.cond, first.lstrip(),
                                           COLOR.clear,
                                           wid=box_width)
            second = "{}{:^{wid}}{}".format(COLOR.cond,
                                            ' '.join(tmp)[:box_width],
                                            COLOR.clear,
                                            wid=box_width)
        return [first, second]

    switch = {'date':           date,
              'weekday':        weekday,
              'dash':           dashed_line,
              'dash_corn':      dashed_with_corners,
              'blank':          blank_line,
              'temp_high_f':    high_temp,
              'temp_low_f':     low_temp,
              'precip':         precip,
              'wind_sd':        wind_speed_dir,
              'conditions':     conditions}
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
        temp = func(day, curr_day, box_width)
        if isinstance(temp, str):
            res.append(temp)
        elif isinstance(temp, list):
            res.extend(temp)
        else:
            raise ValueError("string or list expected, {} returned".format(
                type(temp)))
    return res


def format_header(header_format, label_width, box_width, COLORS):
    head = ' ' * label_width
    for day in ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday']:
        head = "{}{}{:^{wid}}{}".format(head,
                                        COLORS.italic,
                                        day if box_width >= 10 else day[0:3],
                                        COLORS.clear,
                                        wid=box_width)
    res = []
    res.append(head)
    return res


def format_day_list(lis, box_width, box_height, format_list, COLOR):
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
