#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#       file:   print_hourly.py
#     author:   dpomondo
#
#               Called form getter.py
# -----------------------------------------------------------------------------

import sys
import math
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import printers.utilities


def print_hourly(hourly_wdb, frmt='lines'):
    width = printers.utilities.get_terminal_width()
    height = printers.utilities.get_terminal_height()
    if frmt == 'lines':
        res = hourly_by_lines(hourly_wdb, width, height)
    if frmt == 'bars':
        res = hourly_by_bars(hourly_wdb, width, height)
    return res


def hourly_by_lines(hourly_wdb, width, height):
    res = []
    for hour in hourly_wdb:
        compound = "{:>9}, {:>2}:{:<2}".format(
            hour['FCTTIME']['weekday_name'],
            hour['FCTTIME']['hour'],
            hour['FCTTIME']['min'])
        res.append("{:>16}  temp:{:>4}\tconditions: {}".format(
            compound,
            hour['temp']['english'],
            hour['condition']))
    return res


def format_bar_hour(weat_hour, COLOR, zero_hour):
    res = []
    for r in [(('temp', 'english'), COLOR.hot, COLOR.cool),
              (('sky', ), COLOR.hot, COLOR.cool),
              (('pop', ), COLOR.hot, COLOR.cool),
              ]:
        target = weat_hour
        currs = zero_hour
        for z in r[0]:
            target = target[z]
            currs = currs[z]
        res.append('{}{:^6}{}'.format(COLOR.hot if target > currs else
            COLOR.cool if target < currs else COLOR.temp, target, COLOR.clear))
    res.append("{:^6}".format("{}:{}".format(weat_hour['FCTTIME']['hour'],
                                             weat_hour['FCTTIME']['min'])))
    return res


def hourly_by_bars(hourly_wdb, width, height):
    res = [[]]
    fins = []
    COLORS = printers.utilities.get_colors()
    _keys = ["Temp", "Cloud %", "Precip Chance", "Time"]
    for k in _keys:
        res[0].append("{:>{width}}: ".format(k, width=max(
            list(len(z) for z in _keys))))
    for i in range((width - max(list(len(z) for z in res[0])))//6):
        res.append(format_bar_hour(hourly_wdb[i], COLORS, hourly_wdb[0]))
    for i in range(len(res[0])):
        fins.append(''.join(z[i] for z in res))
    return fins


def main():
    """ testing!
    """
    import returner
    now = returner.main()
    print("Testing printing by lines:")
    nerd = print_hourly(now['hourly_forecast'], frmt='lines')
    for lin in nerd:
        print(lin)
    print("Testing bars...")
    nerd = print_hourly(now['hourly_forecast'], frmt='bars')
    for lin in nerd:
        print(lin)


if __name__ == '__main__':
    main()
