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
# import math
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import printers.utilities


def print_hourly(hourly_wdb, sun_wdb, frmt='bars'):
    width = printers.utilities.get_terminal_width()
    height = printers.utilities.get_terminal_height()
    if frmt == 'lines':
        res = hourly_by_lines(hourly_wdb, width, height)
    if frmt == 'bars':
        res = hourly_by_bars(hourly_wdb, width, height, sun_wdb)
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


def bar_temp_color(target, curr, COLOR):
    return (COLOR.hot if target > curr else
            COLOR.cool if target < curr else
            COLOR.temp)


def bar_cloud_color(target, _,  COLOR):
    return (COLOR.cloud25 if target < 25 else
            COLOR.cloud50 if target < 50 else
            COLOR.cloud75 if target < 75 else
            COLOR.cloud100)


def bar_precip_color(target, _,  COLOR):
    return (COLOR.precip25 if target < 25 else
            COLOR.precip50 if target < 50 else
            COLOR.precip75 if target < 75 else
            COLOR.precip100)


def bar_wind_color(target, curr, COLOR):
    return bar_temp_color(target, curr, COLOR)


def format_bar_hour(weat_hour, COLOR, zero_hour, sunrise, sunset):
    res = []
    # the COLOR attrs need to be func returning color codes; this lets each
    # feature have drastically different color logic
    for r in [(('temp', 'english'), bar_temp_color),
              (('sky', ), bar_cloud_color),
              (('pop', ), bar_precip_color),
              (('wspd', 'english'), bar_wind_color)]:
        target = weat_hour
        currs = zero_hour
        for z in r[0]:
            target = target[z]
            currs = currs[z]
        res.append('{}{:^6}{}'.format(r[1](int(target), int(currs), COLOR),
                                      target, COLOR.clear))
    res.append("{}{:^6}{}".format(
        sunrise_sunset_color(weat_hour['FCTTIME']['hour'],
                             sunrise, sunset, COLOR),
        sunrise_sunset_time(weat_hour['FCTTIME']['hour'], sunrise, sunset),
        COLOR.clear))
    res.append("{:^6}".format("{}:{}".format(weat_hour['FCTTIME']['hour'],
                                             weat_hour['FCTTIME']['min'])))
    return res


def sunrise_sunset_color(hour, sunrise, sunset, CLR):
    """ Returns a color code depending on distance from sunrise/sunset

        args:   hour: string representing an hour ('0' to '23')
                sunrise: tuple of two strings, representing hour and minute
                sunset: tuple of two strings, representing hour and minute
                CLR: Color class object created by utilities.get_colors()

        returns:    Color class attribute (a printable color escape code)
                    depending on the difference between the given hour and the
                    hour of sunrise/sunset.
    """
    set_dif = int(hour) - int(sunset[0])
    rise_dif = int(hour) - int(sunrise[0])
    return (CLR.dusk if set_dif > -1 and set_dif <= 1 else
            CLR.dawn if rise_dif >= -1 and rise_dif < 1 else
            CLR.night if rise_dif * set_dif > 0 else
            CLR.day)


def sunrise_sunset_time(hour, sunrise, sunset):
    """ Determines whether a given hour includes sunrise or sunset.

        args:   hour: string indicating an hour ('0' to '23')
                sunrise: tuple of two strings, representing hour and minute
                sunset: tuple of two strings, representing hour and minute

        Returns:    empty string if the given hour does NOT include rise/set,
                    formatted sunrise time if given hour includes sunrise,
                    formatted sunset time if given hour includes sunset
        """
    return ("{}:{}".format(*sunrise) if int(hour) - int(sunrise[0]) == 0
            else
            "{}:{}".format(*sunset) if int(hour) - int(sunset[0]) == 0
            else "")


def hourly_by_bars(hourly_wdb, width, height, sun_wdb):
    res = [[]]
    fins = []
    COLORS = printers.utilities.get_colors(color_flag=True)
    _keys = ["Temp", "Cloud %", "Precip Chance", "Wind speed",
             "Sunrise/set", "Time"]
    for k in _keys:
        res[0].append("{:>{width}}: ".format(k,
                      width=max(list(len(z) for z in _keys))))
    # for i in range((width - max(list(len(z) for z in res[0])))//6):
    for i in range((width - len(res[0][0])) // 6):
        res.append(format_bar_hour(hourly_wdb[i], COLORS, hourly_wdb[0],
                   (sun_wdb['sunrise']['hour'], sun_wdb['sunrise']['minute']),
                   (sun_wdb['sunset']['hour'], sun_wdb['sunset']['minute'])))
    for i in range(len(res[0])):
        fins.append(''.join(z[i] for z in res))
    return fins


def main():
    """ testing!
    """
    import returner
    now = returner.main()
    print("Testing printing by lines:")
    nerd = print_hourly(now['hourly_forecast'], None, frmt='lines')
    for lin in nerd:
        print(lin)
    print("Testing bars...")
    nerd = print_hourly(now['hourly_forecast'], now['sun_phase'], frmt='bars')
    for lin in nerd:
        print(lin)


if __name__ == '__main__':
    main()
