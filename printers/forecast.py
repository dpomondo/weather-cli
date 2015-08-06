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
# max_cols = 5
min_box_width = 20
# box_width = 22


def get_box_size(lens, width):
    max_cols, box_width = None, None
    for i in range(lens, 1, -1):
        temp = math.ceil(lens/i)
        # print("{}: {} --> {}".format(i, temp, temp * min_box_width < width))
        if temp * min_box_width <= width:
            max_cols = temp
            box_width = min_box_width + int(
                (width - (max_cols * min_box_width)) / max_cols)
        else:
            break
    if max_cols is not None:
        return max_cols, box_width
    # `magic` for now
    else:
        tb = sys.exc_info()[2]
        # raise e.with_traceback(tb)
        raise IndexError("{} and {} made get_box_size func fail".format(lens,
            width)).with_traceback(tb)
        # return 5, 22


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


def new_forecast_day_format(forecast_day, box_width):
    """ formats one day of a forecast, returned as a list of lines
    """
    res = []
    margin = (box_width - 20) // 2
    res.append('{}{}'.format('+', '-' * (box_width - 1)))
    res.append('{}'.format(' ' * box_width))
    day = '{}{}, {} {}'.format(' ' * margin, forecast_day['date']['weekday'],
                               forecast_day['date']['monthname'],
                               forecast_day['date']['day'])
    padding = box_width - len(day)
    res.append('{}{}'.format(day, ' ' * padding))
    nerd = '{}{:>10}{}'.format(' ' * margin, 'high: ',
                               forecast_day['high']['fahrenheit'])
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    nerd = '{}{:>10}{}'.format(' ' * margin, 'low: ',
                               forecast_day['low']['fahrenheit'])
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    nerd = '{}{:>10}{}'.format(' ' * margin, 'weather: ',
                               forecast_day['conditions'][:10])
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    res.append(' ' * box_width)
    nerd = '{}{}{}mph {}'.format(' ' * margin, 'wind: ',
                                 forecast_day['avewind']['mph'],
                                 forecast_day['avewind']['dir'])
    padding = box_width - len(nerd)
    res.append('{}{}'.format(nerd, ' ' * padding))
    res.append(' ' * box_width)
    # make the box:
    res2 = []
    res2.append(res[0])
    for lin in res[1:]:
        res2.append( '|' + lin[1:])
    return res2


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
    num_days = len(weat_db)
    width = printers.utilities.get_terminal_width()
    height = printers.utilities.get_terminal_height()
    max_cols, box_width = get_box_size(len(weat_db), width)
    cols = min(max_cols, width//box_width)
    rows = math.ceil(num_days/cols)
    while rows * 9 > height:    # truncate if too long:
        rows -= 1
    res = []
    for c in range(rows):
        res.append([])
        for i in range(9):
            res[c].append(' ' * int((width - (cols * box_width)) / 2))

    # now we build the thing
    for day_index in range(min(rows * max_cols, len(weat_db))):
        # this is the line that fails with small screen sizes( list index out
        # of range):
        # forecast_day_format(weat_db[day_index], res[day_index // cols],
                            # box_width)
        temp = new_forecast_day_format(weat_db[day_index], box_width)
        try:
            for i in range(9):
                res[day_index//cols][i] += temp[i]
        except IndexError as e:
            raise IndexError("day_index: {} cols: {} div: {}".format(day_index,
                cols, day_index//cols)) from e

    # return the result
    # but first flatten:
    res2 = []
    for c in res:
        for lin in c:
            res2.append(lin)
    res2.append(res2[0])
    res3 = []
    for lin in res2:
        res3.append(lin[:-1] + lin[0])
    return res3


if __name__ == '__main__':
    print("Begining test:")
    wids = printers.utilities.get_terminal_height()
    hits = printers.utilities.get_terminal_width()
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
