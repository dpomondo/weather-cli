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
box_width = 22


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


def forecast_day_format(forecast_day, lin_row):
    """ appends a formatted forecast day to a list of strings.
        
        forecast_day:   current['current_response']
                               ['simpleforecast']
                               ['forecast_day']
                               [index]
        lin_row:        res[row_num]

        """
    lin_row[0] = '{}{}'.format(lin_row[0], '-' * box_width)
    lin_row[1] = '{}{}'.format(lin_row[1], ' ' * box_width)
    day = '{}, {} {}'.format(forecast_day['date']['weekday'],
            forecast_day['date']['monthname'], forecast_day['date']['day'])
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
    cols = min(max_cols, width//box_width)
    rows = math.ceil(num_days/cols)
    while rows * 8 > height:
        rows -= 1
    res = []
    for c in range(rows):
        res.append([])
        for i in range(9):
            res[c].append(' ' * int((width - (cols * box_width)) / 2))

    # now we build the thing
    for day_index in range(len(weat_db)):
        forecast_day_format(weat_db[day_index], res[day_index // cols])

    # return the result
    # but first flatten:
    res2 = []
    for c in res:
        for lin in c:
            res2.append(lin)
    return res2
    # for lin in res2:
        # print(lin)


if __name__ == '__main__':
    print(printers.utilities.get_terminal_height())
    print(printers.utilities.get_terminal_width())
