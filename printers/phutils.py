def time_format_generator(hourly_wdb, header, head_width, col_width,
                          color_func=lambda x: "", CLEAR="", *args):
    """ generates a sequence of formated times from a list of times
    """
    ind = -1
    import utils.utilities as utils
    while ind < len(hourly_wdb):
        if ind < 0:
            temp = "{:>{wid}}: ".format(header, wid=head_width)
        else:
            hr = utils.eat_keys(hourly_wdb[ind], ('FCTTIME', 'hour'))
            mn = utils.eat_keys(hourly_wdb[ind], ('FCTTIME', 'min'))
            _tim = "{:>{wid}}".format("{}:{}".format(hr, mn), wid=col_width)
            temp = ""
            for zind in range(col_width):
                temp_mins = int(60 * (zind / col_width))
                #  temp_color = color_func((hr, temp_mins), *args)
                temp_color = color_func((hr, temp_mins), *args)
                temp = "{}{}{}{}".format(temp, temp_color, _tim[zind], CLEAR)
        yield temp
        ind += 1


def indexer_maker(start, col_width=6):
    """ returns a function to determine the index of an item.

        start:      start time, as a tuple: ("hour", "min")
        target:     item time, as a tuple
        header:     length of header
        col_width:  how wide each item will be in the final string
    """
    start_hour, start_min = int(start[0]), int(start[1])

    def index(hour, minute, col_width):
        return hour * col_width + int(minute // (60 / col_width))

    def maker(target):
        """ input: tuple (or list) -> ("hour", "min")
        """
        if len(target) > 1:
            target_hour, target_min = int(target[0]), int(target[1])
        else:
            target_hour, target_min = int(target), 0
        start_ind = index(start_hour, start_min, col_width)
        target_ind = index(target_hour, target_min, col_width)
        res = target_ind - start_ind
        if res >= 0:
            return res
        else:
            return target_ind + (index(24, 0, col_width) - start_ind)
    return maker


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


def new_sunrise_line(hourly_wdb, sun_wdb, COLORS, col_width, head):
    # kill the following...
    import utils.utilities as utils
    import printers.colorfuncs as cf
    _hour_lis = list(utils.eat_keys(hour, ('FCTTIME', 'hour')) for hour in
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
    #  color_func = cf.sunrise_sunset_color
    color_func = cf.new_sunrise_sunset_color
    while index < tar_length:
        curr_hour = _hour_lis[index // col_width]
        curr_min = (index % col_width) * 10
        if index == sunrise_index:
            temp = "{}{}{}".format(temp,
                                   color_func((curr_hour, curr_min),
                                              (sunrise_hour, sunrise_min),
                                              (sunset_hour, sunset_min),
                                              COLORS),
                                   sunrise_str[0])
            sunrise_str = sunrise_str[1:]
            index += 1
            if len(sunrise_str) > 0:
                sunrise_index += 1
        elif index == sunset_index:
            temp = "{}{}{}".format(temp,
                                   color_func((curr_hour, curr_min),
                                              (sunrise_hour, sunrise_min),
                                              (sunset_hour, sunset_min),
                                              COLORS),
                                   sunset_str[0])
            sunset_str = sunset_str[1:]
            index += 1
            if len(sunset_str) > 0:
                sunset_index += 1
        else:
            temp = "{}{}{}".format(temp,
                                   color_func((curr_hour, curr_min),
                                              (sunrise_hour, sunrise_min),
                                              (sunset_hour, sunset_min),
                                              COLORS),
                                   " ")
            index += 1
    temp += COLORS.clear
    return temp


def sunrise_line(hourly_wdb, sun_wdb, COLORS, col_width, head):
    import printers.colorfuncs as cf
    temp = "{:>{wid}}: ".format("Sunrise/set", wid=head)
    for hour in hourly_wdb:
        temp = ("{}{}{:>{wid}}{}".format(temp,
                cf.sunrise_sunset_color(hour['FCTTIME']['hour'],
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



