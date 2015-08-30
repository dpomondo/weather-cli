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
#  import math
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import printers.utilities


def print_hourly(hourly_wdb, sun_wdb, frmt='bars'):
    width = printers.utilities.get_terminal_width()
    height = printers.utilities.get_terminal_height()
    COLORS = printers.utilities.get_colors(color_flag=True)
    if frmt == 'lines':
        res = hourly_by_lines(hourly_wdb, width, height)
    elif frmt == 'bars':
        res = hourly_by_bars(hourly_wdb, width, height, sun_wdb, COLORS)
    elif frmt == 'cols':
        res = hourly_by_cols(hourly_wdb, width, height, sun_wdb, COLORS,
                             col_width=6)
    else:
        res = hourly_by_lines(hourly_wdb, width, height)
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


def sunrise_sunset_color(tim, sunrise, sunset, CLR):
    """ Returns a color code depending on distance from sunrise/sunset

        args:   hour: string representing an hour ('0' to '23')
                sunrise: tuple of two strings, representing hour and minute
                sunset: tuple of two strings, representing hour and minute
                CLR: Color class object created by utilities.get_colors()

        returns:    Color class attribute (a printable color escape code)
                    depending on the difference between the given hour and the
                    hour of sunrise/sunset.
    """
    if (isinstance(tim, tuple) or isinstance(tim, list)) and len(tim) == 2:
        hour, minute = int(tim[0]), round(int(tim[1]))
    elif isinstance(tim, int) or isinstance(tim, str):
        hour, minute = int(tim), 0
    else:
        raise ValueError("sunrise_sunset_colr passed bad value")
    set_hour_dif = hour - int(sunset[0])
    set_min_dif = minute - round(int(sunset[1]) / 10) * 10
    rise_hour_dif = hour - int(sunrise[0])
    rise_min_dif = minute - round(int(sunrise[1]) / 10) * 10
    if set_hour_dif == 0 and set_min_dif >= -10:
        return CLR.dusk
    elif set_hour_dif > 0 and set_hour_dif < 2:
        return CLR.dusk
    elif set_hour_dif == 2 and set_min_dif <= 0:
        return CLR.dusk
    elif rise_hour_dif == -2 and rise_min_dif >= 0:
        return CLR.dawn
    elif rise_hour_dif > -2 and rise_hour_dif < 0:
        return CLR.dawn
    elif rise_hour_dif == 0 and rise_min_dif <= 0:
        return CLR.dawn
    elif set_hour_dif * rise_hour_dif > 0:
        return CLR.night
    else:
        return CLR.day


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


def format_bar(color_func, target, curr, COLOR, width):
    """ returns a formatted string with color escape codes
    """
    return "{}{:^{wid}}{}".format(color_func(target, curr, COLOR),
                                  target, COLOR.clear, wid=width)


def format_bar_hour(weat_hour, COLOR, zero_hour, sunrise, sunset):
    """ return a vertical set of strings, one hour of info
    """
    res = []
    for r in [(('temp', 'english'), bar_temp_color),
              (('sky', ), bar_cloud_color),
              (('pop', ), bar_precip_color),
              (('wspd', 'english'), bar_wind_color)]:
        target = eat_keys(weat_hour, r[0])
        currs = eat_keys(zero_hour, r[0])
        res.append(format_bar(r[1], int(target), int(currs), COLOR, width=6))
    # TODO: if sunrise_sunset_color can get wrangled into the standard
    # color_func api, we can move this to a format_bar call:
    res.append("{}{:^6}{}".format(
        sunrise_sunset_color(weat_hour['FCTTIME']['hour'],
                             sunrise, sunset, COLOR),
        sunrise_sunset_time(weat_hour['FCTTIME']['hour'], sunrise, sunset),
        COLOR.clear))
    res.append("{:^6}".format("{}:{}".format(weat_hour['FCTTIME']['hour'],
                                             weat_hour['FCTTIME']['min'])))
    return res


def hourly_by_bars(hourly_wdb, width, height, sun_wdb, COLORS, col_width=6):
    """ for each hour, return a vertical set of strings with the formatted info
    """
    res = [[]]
    fins = []
    _keys = ["Temp", "Cloud %", "Precip Chance", "Wind speed",
             "Sunrise/set", "Time"]
    for k in _keys:
        res[0].append("{:>{width}}: ".format(k,
                      width=max(list(len(z) for z in _keys))))
    # for i in range((width - max(list(len(z) for z in res[0])))//6):
    for i in range((width - len(res[0][0])) // col_width):
        res.append(format_bar_hour(hourly_wdb[i], COLORS, hourly_wdb[0],
                   (sun_wdb['sunrise']['hour'], sun_wdb['sunrise']['minute']),
                   (sun_wdb['sunset']['hour'], sun_wdb['sunset']['minute'])))
    for i in range(len(res[0])):
        fins.append(''.join(z[i] for z in res))
    return fins


def eat_keys(_lis, _key_tup):
    """ helper func
    """
    tar = _lis
    for k in _key_tup:
        tar = tar[k]
    return tar


def new_hourly_by_cols():
    """ inputs:
        format_dict ->  specifies the order in which data functions get
                        called.
                        form:
                            {1: "Temp",
                                2: "Cloud Cover"... etc}
                        use:
                        for n in range(len(format_dict)):
                            function_dict[format_dict[n]]
        function_dict -> specifies the function and parameters for each
                        data function call.
                        form:
                            {"Temp": (temp_func, [db, color_func...]),
                            {"Cloud Cover": (cloud_func, db, [...]),
                                etc... }
                        use:
                            function_dict["xxx"][0](*function_dict["xxx"](1))
                        example:
                            "Temp": (cols_formater, [_lis[:ind_slice], ...])

    """
    pass


def hourly_by_cols(hourly_wdb, width, height, sun_wdb, COLORS, col_width=5):
    """ for each bit of info, format the entire horizontal string at once

        And yes, that means `hourly_by_cols` and `hourly_by_bars` are named
        exactly backwards...
    """
    # begin main functioning!
    res = []
    _keys = ["Temp", "Cloud %", "Precip Chance", "Wind speed",
             "Sunrise/set", "Time"]
    head = max(list(len(z) for z in _keys))
    ind_slice = (width - head - 2) // col_width
    # # build the time string -- top
    #  temp = "{:>{wid}}: ".format("Time", wid=head)
    #  for hour in hourly_wdb[:ind_slice]:
        #  temp = "{}{:^{wid}}".format(temp, "{}:{}".format(
            #  eat_keys(hour, ('FCTTIME', 'hour')),
            #  eat_keys(hour, ('FCTTIME', 'min'))), wid=col_width)
    #  res.append(temp)
    # build the basic info strings
    for r in [("Temp", ('temp', 'english'), bar_temp_color, 11),
              ("Cloud %", ('sky', ), bar_cloud_color, 1),
              ("Precip Chance", ('pop', ), bar_precip_color, 1),
              ("Wind speed", ('wspd', 'english'), bar_wind_color, 1)]:
        _lis = list(eat_keys(hour, r[1]) for hour in hourly_wdb)
        temp, star_ind = cols_formatter(_lis[:ind_slice],
                                        COLORS, r[2], r[3], col_width)
        for lin in range(len(temp)):
            res.append("{}{}".format("{:>{wid}}{}".format(r[0], ": ", wid=head)
                       if lin == star_ind else " " * (head + 2), temp[lin]))
    # bnuild the sunrise/sunset string
    temp = sunrise_line(hourly_wdb[:ind_slice], sun_wdb, COLORS,
                        col_width=6, head=head)
    res.append(temp)
    temp = new_sunrise_line(hourly_wdb[:ind_slice], sun_wdb, COLORS,
                            col_width=6, head=head)
    res.append(temp)
    # build the time string
    temp = "{:>{wid}}: ".format("Time", wid=head)
    for hour in hourly_wdb[:ind_slice]:
        temp = "{}{:>{wid}}".format(temp, "{}:{}".format(
            eat_keys(hour, ('FCTTIME', 'hour')),
            eat_keys(hour, ('FCTTIME', 'min'))), wid=col_width)
    res.append(temp)
    #  insert a line before and after? No... let's not
    #  res.insert(0, '-' * (head + col_width * ind_slice))
    #  res.append('-' * (head + col_width * ind_slice))
    # return the result!
    return res


def new_sunrise_line(hourly_wdb, sun_wdb, COLORS, col_width, head):
    _hour_lis = list(eat_keys(hour, ('FCTTIME', 'hour')) for hour in
                     hourly_wdb)
    _min_lis = list(eat_keys(hour, ('FCTTIME', 'min')) for hour in
                    hourly_wdb)
    temp = "{:>{wid}}: ".format("Sunrise/set", wid=head)
    sunrise_hour = sun_wdb['sunrise']['hour']
    sunrise_min = sun_wdb['sunrise']['minute']
    if sunrise_hour in _hour_lis:
        sunrise_index = ((_hour_lis.index(sunrise_hour) * col_width)
                         + int(sunrise_min) // 10)
    else:
        sunrise_index = -1
    sunset_hour = sun_wdb['sunset']['hour']
    sunset_min = sun_wdb['sunset']['minute']
    if sunset_hour in _hour_lis:
        sunset_index = ((_hour_lis.index(sunset_hour) * col_width)
                        + int(sunset_min) // 10)
    else:
        sunset_index = -1
    sunrise_str = "{}:{}".format(sunrise_hour, sunrise_min)
    sunset_str = "{}:{}".format(sunset_hour, sunset_min)
    index = 0
    tar_length = col_width * len(hourly_wdb)
    while index < tar_length:
        curr_hour = _hour_lis[index // col_width]
        curr_min = (index % col_width) * 10
        if index == sunrise_index:
            temp = "{}{}{}".format(temp,
                                   sunrise_sunset_color((curr_hour, curr_min),
                                                        (sunrise_hour,
                                                         sunrise_min),
                                                        (sunset_hour,
                                                         sunset_min),
                                                        COLORS),
                                   sunrise_str[0])
            sunrise_str = sunrise_str[1:]
            index += 1
            if len(sunrise_str) > 0:
                sunrise_index += 1
        elif index == sunset_index:
            temp = "{}{}{}".format(temp,
                                   sunrise_sunset_color((curr_hour, curr_min),
                                                        (sunrise_hour,
                                                         sunrise_min),
                                                        (sunset_hour,
                                                         sunset_min),
                                                        COLORS),
                                   sunset_str[0])
            sunset_str = sunset_str[1:]
            index += 1
            if len(sunset_str) > 0:
                sunset_index += 1
        else:
            temp = "{}{}{}".format(temp,
                                   sunrise_sunset_color(curr_hour,
                                                        (sunrise_hour,
                                                         sunrise_min),
                                                        (sunset_hour,
                                                         sunset_min),
                                                        COLORS),
                                   " ")
            index += 1
    temp += COLORS.clear
    return temp


def sunrise_line(hourly_wdb, sun_wdb, COLORS, col_width, head):
    temp = "{:>{wid}}: ".format("Sunrise/set", wid=head)
    for hour in hourly_wdb:
        temp = ("{}{}{:>{wid}}{}".format(temp,
                sunrise_sunset_color(hour['FCTTIME']['hour'],
                                     (sun_wdb['sunrise']['hour'],
                                     sun_wdb['sunrise']['minute']),
                                     (sun_wdb['sunset']['hour'],
                                     sun_wdb['sunset']['minute']),
                                     COLORS),
                sunrise_sunset_time(hour['FCTTIME']['hour'],
                                    (sun_wdb['sunrise']['hour'],
                                    sun_wdb['sunrise']['minute']),
                                    (sun_wdb['sunset']['hour'],
                                    sun_wdb['sunset']['minute'])),
                COLORS.clear, wid=col_width))
    return temp


def cols_formatter(_l, COLOR, color_func, col_height=11, col_width=6):
    def indexer(_x):
        # return height - math.floor((_x - mn) / diff * height)
        # return (height - 1) - math.floor((_x - mn) / diff * (height - 1))
        # return (height - 1) - math.ceil((_x - mn) / diff * (height - 1))
        # return (height - 1) - round((_x - mn) / diff * (height - 1))
        if col_height > 1 and diff > 0:
            return (col_height - 1) - int((_x - mn) / diff * (col_height - 1))
        else:
            return 0
    l = list(map(int, _l))
    res = []
    start = l[0]
    mx = max(l)
    mn = min(l)
    diff = mx - mn
    #  rng = diff / height
    #  print("min: {} max: {} diff: {}".format(mn, mx, diff))
    for i in range(col_height):
        res.append("")
    star_index = indexer(start)
    for num in l:
        index = indexer(num)
        for j in range(col_height):
            zing = ""
            if j == index:
                zing = color_func(num, start, COLOR), num, COLOR.clear
            elif j > index and j <= star_index:
                zing = color_func(num, start, COLOR), "++", COLOR.clear
            elif j < index and j >= star_index:
                zing = color_func(num, start, COLOR), "--", COLOR.clear
            else:
                zing = COLOR.clear, "", COLOR.clear
            res[j] += "{}{:^{wid}}{}".format(*zing, wid=col_width)
    return res, star_index


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
    print("Testing cols...")
    # COLORS = printers.utilities.get_colors(color_flag=True)
    # width = printers.utilities.get_terminal_width()
    # zing = list(z['temp']['english'] for z in now['hourly_forecast'])
    # nerd = cols_formatter(zing[:width//6], COLORS, bar_temp_color)
    nerd = print_hourly(now['hourly_forecast'], now['sun_phase'], frmt='cols')
    for lin in nerd:
        print(lin)


if __name__ == '__main__':
    main()
