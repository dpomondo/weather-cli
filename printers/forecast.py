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
import utils.utilities

# here we have the `magic` numbers, these will eventually be set in a
# config file
# max_cols = 5
min_box_width = 20
# box_width = 22


def get_box_size(lens, width):
    max_cols, box_width = None, None
    for i in range(lens, 1, -1):
        temp = math.ceil(lens/i)
        if temp * min_box_width <= width - (temp + 1):
            max_cols = temp
            box_width = min_box_width + int(
                ((width - (temp + 1)) - (max_cols * min_box_width)) / max_cols)
        else:
            break
    if max_cols is not None:
        return max_cols, box_width
    else:
        tb = sys.exc_info()[2]
        # raise e.with_traceback(tb)
        raise IndexError("{} and {} made get_box_size func fail".format(lens,
                         width)).with_traceback(tb)


def print_forecast(weat_db, frmt='lines'):
    if frmt == 'lines':
        res = lines_forecast(weat_db)
    elif frmt == 'grid':
        res = grid_forecast(weat_db)
    else:
        res = lines_forecast(weat_db)
    return res


def lines_forecast(weat_db):
    res = []
    for day in weat_db:
        res.append("{}, {} {}:\thigh of {}, low of {}, {}".format(
            day['date']['weekday'],
            day['date']['monthname'],
            day['date']['day'],
            day['high']['fahrenheit'],
            day['low']['fahrenheit'],
            day['conditions']))
    return res


def forecast_line_format(box_width, *args):
    """ formats a list of strs to a length, accounting for non-printing chars
    """
    res = ''
    margin = (box_width - 20) // 2
    running_total = margin
    res += ' ' * margin
    for arg in args:
        if isinstance(arg, str):
            res += arg
            if not arg.startswith('\033'):
                running_total += len(arg)
        if isinstance(arg, list):
            for smarg in arg:
                res += str(smarg)
                if not str(smarg).startswith('\033'):
                    running_total += len(str(smarg))
    res += ' ' * (box_width - running_total)
    return res


def new_new_forecast_day_format(forecast_day, box_width, today_h, today_l,
                                COLORS):
    """ formats one day of a forecast, returned as a list of lines
    """
    res = []
    # margin = (box_width - 20) // 2
    # res.append('{}{}'.format('+', '-' * (box_width - 1)))
    # TODO: each line requires a call to a formatting func, passed the COLORS,
    # the label, and the forecast_day keys. Func totals up the length of the
    # text to determine padding, THEN does the formatting and returns the line.
    # This will fix the issue where the COLORS info is counted when determining
    # the length of the text for end padding
    this_h = forecast_day['high']['fahrenheit']
    this_l = forecast_day['low']['fahrenheit']
    lines = [[''],
             [forecast_day['date']['weekday'], ', ',
              forecast_day['date']['monthname'], ' ',
              forecast_day['date']['day']],
             ['{:>10}'.format('high: '),
              COLORS.hot if this_h > today_h else
              COLORS.cool if this_h < today_h else COLORS.high,
              forecast_day['high']['fahrenheit'], COLORS.clear],
             ['{:>10}'.format('low: '),
              COLORS.hot if this_l > today_l else
              COLORS.cool if this_l < today_l else COLORS.low,
              forecast_day['low']['fahrenheit'], COLORS.clear],
             ['{:>10}'.format('wind: '), COLORS.wind,
              forecast_day['avewind']['mph'],
              forecast_day['avewind']['dir'],
              COLORS.clear],
             ['']
             ]
    # Here we have to react to the unpredictable:
    if len(forecast_day['conditions']) <= 10:
        lines.insert(4, ['{:>10}'.format('weather: '), COLORS.cond,
                         forecast_day['conditions'][:10], COLORS.clear])
        lines.insert(5, [''])
    elif len(forecast_day['conditions']) <= 20:
        lines.insert(4, ['{:>10}'.format('weather: '), COLORS.clear])
        lines.insert(5, [COLORS.cond,
                         '{:>{width}}'.format(forecast_day['conditions'][:20],
                                              width=20),
                         COLORS.clear])
    else:
        first_line = ''
        second_line = forecast_day['conditions'][:box_width].split()
        while len(first_line) < 10:
            first_line += second_line[0] + ' '
            second_line = second_line[1:]
        second_line = ' '.join(second_line)
        lines.insert(4, ['{:>10}'.format('weather: '), COLORS.cond,
                         first_line, COLORS.clear])
        lines.insert(5, [COLORS.cond, '{:>20}'.format(second_line),
                         COLORS.clear])
    for lin in lines:
        res.append(forecast_line_format(box_width, lin))
    return res


def new_forecast_day_format(forecast_day, box_width, COLORS):
    """ formats one day of a forecast, returned as a list of lines
    """
    res = []
    margin = (box_width - 20) // 2
    # res.append('{}{}'.format('+', '-' * (box_width - 1)))
    # TODO: each line requires a call to a formatting func, passed the COLORS,
    # the label, and the forecast_day keys. Func totals up the length of the
    # text to determine padding, THEN does the formatting and returns the line.
    # This will fix the issue where the COLORS info is counted when determining
    # the length of the text for end padding
    res.append('{}'.format(' ' * box_width))
    day = '{}{}, {} {}'.format(' ' * margin, forecast_day['date']['weekday'],
                               forecast_day['date']['monthname'],
                               forecast_day['date']['day'])
    padding = box_width - len(day)
    res.append('{}{}'.format(day, ' ' * padding))
    nerd = '{}{:>10}{}{}{}'.format(' ' * margin, 'high: ', COLORS.high,
                                   forecast_day['high']['fahrenheit'],
                                   COLORS.clear)
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    nerd = '{}{:>10}{}{}{}'.format(' ' * margin, 'low: ', COLORS.low,
                                   forecast_day['low']['fahrenheit'],
                                   COLORS.clear)
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    nerd = '{}{:>10}{}{}{}'.format(' ' * margin, 'weather: ', COLORS.cond,
                                   forecast_day['conditions'][:10],
                                   COLORS.clear)
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    res.append(' ' * box_width)
    nerd = '{}{}{}{}mph {}{}'.format(' ' * margin, 'wind: ', COLORS.wind,
                                     forecast_day['avewind']['mph'],
                                     forecast_day['avewind']['dir'],
                                     COLORS.clear)
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    res.append(' ' * box_width)
    return res


def add_box_lines(lins, day_num, total_days, cols_nums):
    """ Add grid lines to a list of lines, depending on place in grid.

        lins: list of lines formatted using new_forecast_day_format(...)
        day_num: place in list of days
        total_days: total number of days getting formatted
        cols_nums: total number of columns in the grid.

        always............................. left, bottom
        If day_num < cols_nums............. top
        if day_num +1  % cols_nums ==0 .... right
        if day_num = total_days - 1........ right
        """
    new_lins = []
    left_marker = '+'
    left_vertical = '|'
    grid_line = '-' * len(lins[0])
    if ((day_num + 1) % cols_nums == 0) or (day_num + 1 == total_days):
        right_vertical = '|'
        right_marker = '+'
    else:
        right_vertical, right_marker = '', ''
    # left, maybe right:
    for lin in lins:
        new_lins.append("{}{}{}".format(left_vertical, lin,
                                        right_vertical))
    # bottom:
    new_lins.append("{}{}{}".format(left_marker, grid_line, right_marker))
    # top:
    if day_num < cols_nums:
        new_lins.insert(0, new_lins[-1])
    return new_lins


def forecast_day_format(forecast_day, lin_row, box_width):
    """ this function is deprecated and slated for obliteration
        """
    lin_row[0] = '{}{}{}'.format(lin_row[0], '+', '-' * (box_width-1))
    lin_row[1] = '{}{}'.format(lin_row[1], ' ' * box_width)
    day = '{}, {} {}'.format(forecast_day['date']['weekday'],
                             forecast_day['date']['monthname'],
                             forecast_day['date']['day'])
    padding = box_width - len(day)
    lin_row[2] = '{}{}{}'.format(lin_row[2], day, ' ' * padding)
    nerd = '{:>10}{}'.format('high: ', forecast_day['high']['fahrenheit'])
    padding = box_width - len(nerd)
    lin_row[3] = '{}{}{}'.format(lin_row[3], nerd, ' ' * padding)
    nerd = '{:>10}{}'.format(' low: ', forecast_day['low']['fahrenheit'])
    padding = box_width - len(nerd)
    lin_row[4] = '{}{}{}'.format(lin_row[4], nerd, ' ' * padding)
    nerd = '{:>10}{}'.format('weather: ', forecast_day['conditions'][:10])
    padding = box_width - len(nerd)
    lin_row[5] = '{}{}{}'.format(lin_row[5], nerd, ' ' * padding)
    lin_row[6] = ' ' * box_width
    nerd = '{}{}mph {}'.format('wind: ', forecast_day['avewind']['mph'],
                               forecast_day['avewind']['dir'])
    padding = box_width - len(nerd)
    lin_row[7] = '{}{}{}'.format(lin_row[7], nerd, ' ' * padding)
    lin_row[8] = ' ' * box_width


def grid_forecast(weat_db):
    # first, initialize all the vars
    color_flag = True   # this will eventually get set in a config file
    num_days = len(weat_db)
    width = utils.utilities.get_terminal_width()
    height = utils.utilities.get_terminal_height()
    COLORS = utils.utilities.get_colors(color_flag=color_flag)
    max_cols, box_width = get_box_size(len(weat_db), width)
    cols = min(max_cols, width//box_width)
    rows = math.ceil(num_days/cols)
    while rows * 9 > height:    # truncate if too long:
        rows -= 1
    res = []
    for c in range(rows):
        res.append([])

    # now we build the thing
    day_nums = min(rows * max_cols, len(weat_db))
    for day_index in range(day_nums):
        # if the start of a row the whole list gets popped on there...
        if len(res[day_index//cols]) == 0:
            res[day_index//cols] = add_box_lines(
                new_new_forecast_day_format(weat_db[day_index], box_width,
                                            weat_db[0]['high']['fahrenheit'],
                                            weat_db[0]['low']['fahrenheit'],
                                            COLORS),
                day_index, day_nums, cols)
        # or we have to add line by line
        else:
            temp = add_box_lines(new_new_forecast_day_format(
                weat_db[day_index], box_width,
                weat_db[0]['high']['fahrenheit'],
                weat_db[0]['low']['fahrenheit'],
                COLORS),
                day_index, day_nums, cols)
            for lin in range(len(temp)):
                res[day_index//cols][lin] += temp[lin]

    # return the result
    # but first flatten, and add padding:
    padding = ' ' * ((width - len(res[0][0])) // 2)
    res2 = []
    for c in res:
        for lin in c:
            res2.append(padding + lin)
    return res2


if __name__ == '__main__':
    print("Begining test:")
    wids = utils.utilities.get_terminal_height()
    hits = utils.utilities.get_terminal_width()
    print("Screen width: {}\nScreen height :{}".format(wids, hits))
    print("-" * 80)
    print("Testing get_box_size function (this WILL end in an exception):")
    screens = [140, 120, 80, 60, 59, 40, 0]
    days = [10, 12, 15, 5]
    try:
        for size in screens:
            for day in days:
                mc, bw = get_box_size(day, size)
                print("{}: {:>5} {}: {:>3} {}: {:>3} {}: {:>4} {}: {}".format(
                    "Window width:",
                    size,
                    "Days in forcast",
                    day,
                    "max_cols",
                    mc,
                    "box_width",
                    bw,
                    "Columns used",
                    mc * bw))
    except IndexError as e:
        print("Exception correctly caught: \n\t{}".format(e))
        print("-" * 80)
        raise e
