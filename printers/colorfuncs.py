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


def inch_precip_color(target, _,  COLOR):
    return (COLOR.precip25 if target == 0.0 else
            COLOR.precip50 if target < 1.0 else
            COLOR.precip75 if target < 2.5 else
            COLOR.precip100)


def bar_wind_color(target, curr, COLOR):
    return bar_temp_color(target, curr, COLOR)


def alternating_background(target, test_func, COLOR):
    if ((isinstance(target, tuple) or isinstance(target, list)) and
            len(target)) == 2:
        hour, minute = int(target[0]), round(int(target[1]))
    elif isinstance(target, int) or isinstance(target, str):
        hour, minute = int(target), 0
    else:
        raise ValueError("{} passed bad value".format(__name__))
    return COLOR.grey_background if test_func(hour, minute) else COLOR.clear


def new_sunrise_sunset_color(target, sunrise, sunset, COLOR, col_width=6):
    """ Returns a color code depending on distance from sunrise/sunset
    """
    import sys
    if '/usr/self/weather' not in sys.path:
        sys.path.append('/usr/self/weather/')
    import printers.phutils as phutils
    import utils.utilities
    if ((isinstance(target, tuple) or isinstance(target, list)) and
            len(target)) == 2:
        hour, minute = int(target[0]), round(int(target[1]))
    elif isinstance(target, int) or isinstance(target, str):
        hour, minute = int(target), 0
    else:
        raise ValueError("sunrise_sunset_color passed bad value")
    zero_hour = phutils.indexer_maker(('0', '0'))
    rise_ind = zero_hour(sunrise)
    set_ind = zero_hour(sunset)
    time_ind = zero_hour((hour, minute))
    set_diff = set_ind - time_ind
    rise_diff = rise_ind - time_ind
    if set_diff <= 0 and set_diff > -2 * col_width:
        return COLOR.dusk
    elif rise_diff > 0 and rise_diff <= 2 * col_width:
        return COLOR.dawn
    elif rise_diff * set_diff > 0:
        return COLOR.night
    else:
        return COLOR.day


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
