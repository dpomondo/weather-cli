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
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import utils.utilities as utils


def print_forecast(weat_db, frmt='lines', screen_width=None):
    if screen_width is None:
        screen_width = utils.get_terminal_width()
    if frmt == 'lines':
        res = lines_forecast(weat_db)
    elif frmt == 'grid':
        import printers.forecast_grid as fg
        res = fg.grid_forecast(weat_db, screen_width)
    elif frmt == 'week':
        import printers.forecast_week as fw
        res = fw.week_forecast(weat_db, screen_width)
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


if __name__ == '__main__':
    import forecast_grid
    print("Running test from forecast_grid.main...")
    forecast_grid.main()
