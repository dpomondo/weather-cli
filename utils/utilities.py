#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#       file:   utilities.py
#     author:   dpomondo
#
#               Called from getter.py
# -----------------------------------------------------------------------------

import subprocess


def get_terminal_info(arg):
    """ does what it says: returns terminal info given by arg.

    Stolen from:
    http://www.brandonrubin.me/2014/03/18/python-snippet-get-terminal-width/
    """
    command = ['tput', arg]
    try:
        result = int(subprocess.check_output(command))
    except OSError as e:
        print("Invalid Command '{0}': exit status ({1})".format(
              command[0], e.errno))
    except subprocess.CalledProcessError as e:
        print("Command '{0}' returned non-zero exit status: ({1})".format(
              command, e.returncode))
    else:
        return result


def get_terminal_height():
    return get_terminal_info('lines')


def get_terminal_width():
    return get_terminal_info('cols')


def eat_keys(_lis, _key_tup):
    """ helper func
    """
    tar = _lis
    for k in _key_tup:
        tar = tar[k]
    return tar


def get_colors(color_flag=True):
    """ Return object with color information.
    """
    class Colors:
        pass
    colors = Colors()
    # # if color_flag is False:
    #     # color_info = {'temp':  '',
    #                   # 'wind':  '',
    #                   # 'high':  '',
    #                   # 'low':   '',
    #                   # 'cond':  '',
    #                   # 'clear': '',
    #                   # 'hot':   '',
    #                   # 'cool':  '',
    #                   # 'night': '',
    #                   # 'dusk':  '',
    #                   # 'dawn':  '',
    #                   # 'day':   ''}
    # # else:
    #     # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    #     # \033[_;__;__m     --> first:  character effect
    #     #                       second: foreground color
    #     #                       third:  background color
    #     # \033[38;5;___m    --> extended foreground color (0...255)
    #     # \033[48;5;___m    --> extended background color (0...255)
    color_info = {'temp':  "\033[1;34;47m",
                  'wind':  "\033[38;5;199m\033[48;5;157m",
                  'high':  "\033[1;34;47m",
                  'low':   "\033[1;34;47m",
                  'cond':  "\033[3;36;47m",
                  'clear': "\033[0m",
                  'hot':   "\033[38;5;160m\033[48;5;007m",
                  'cool':  "\033[38;5;020m\033[48;5;155m",
                  'night': "\033[38;5;015m\033[48;5;017m",
                  'dusk':  "\033[38;5;015m\033[48;5;020m",
                  'dawn':  "\033[38;5;000m\033[48;5;172m",
                  'day':   "\033[38;5;000m\033[48;5;226m",
                  'cloud25':    "\033[38;5;015m\033[48;5;012m",
                  'cloud50':    "\033[38;5;015m\033[48;5;067m",
                  'cloud75':    "\033[38;5;015m\033[48;5;246m",
                  'cloud100':   "\033[38;5;018m\033[48;5;255m",
                  'precip25':   "\033[38;5;232m\033[48;5;255m",
                  'precip50':   "\033[38;5;238m\033[48;5;255m",
                  'precip75':   "\033[38;5;250m\033[48;5;232m",
                  'precip100':  "\033[38;5;255m\033[48;5;232m",
                  'grey_background': "\033[38;5;233m\033[48;5;251m"
                  }

    for key in color_info.keys():
        if color_flag is True:
            setattr(colors, key, color_info[key])
        elif color_flag is False:
            setattr(colors, key, '')
        else:
            raise KeyError("color_flag is unset")
    return colors


def max_len(_lis):
    """ returns the max length of the items in a list
    """
    return max(list(len(x) for x in _lis))


def time_format_generator(hourly_wdb, header, head_width, col_width,
                          color_func=lambda x: "", CLEAR="", *args):
    """ generates a sequence of formated times from a list of times
    """
    #  import printers.colorfuncs as cf
    res = []
    res.append("{:>{wid}}: ".format(header, wid=head_width))
    #  color_func = cf.new_sunrise_sunset_color
    for hour in hourly_wdb:
        hr = eat_keys(hour, ('FCTTIME', 'hour'))
        mn = eat_keys(hour, ('FCTTIME', 'min'))
        _tim = "{:>{wid}}".format("{}:{}".format(hr, mn), wid=col_width)
        temp = ""
        for zind in range(col_width):
            temp_mins = int(60 * (zind / col_width))
            #  temp_color = color_func((hr, temp_mins), *args)
            temp_color = color_func((hr, temp_mins), *args)
            temp = "{}{}{}{}".format(temp, temp_color, _tim[zind], CLEAR)
        res.append(temp)
    ind = 0
    while ind < len(res):
        yield res[ind]
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
    #  import utils.utilities
    import printers.colorfuncs as cf
    _hour_lis = list(eat_keys(hour, ('FCTTIME', 'hour')) for hour in
                     hourly_wdb)
    #  _min_lis = list(eat_keys(hour, ('FCTTIME', 'min')) for hour in
                    #  hourly_wdb)
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


def main():
    # test width func
    width = get_terminal_width()
    if width:
        print("{}: {}".format("width", width))

    # test height func
    height = get_terminal_height()
    if height:
        print("{}: {}".format("height", height))

    # test indexer_maker
    col_width = 6
    hours = list(str(x) for x in range(24))
    mins = list("{:0>2}".format(x) for x in range(60))
    import random
    r = random.randint(0, len(hours))
    heads = hours[r:] + hours[:r]
    #  heads = hours
    lis_len = (width - 8) // col_width
    header = " " * 8
    for tim in heads[:lis_len]:
        header = "{}{:-<{wid}}".format(header, "{}:{}".format(tim, "00"),
                                       wid=col_width)
    nerd = []
    for i in range(10):
        nerd.append((random.choice(hours), random.choice(mins)))
    worker = indexer_maker((heads[0], "00"), col_width=col_width)
    zerd = []
    for tim in nerd:
        temp = "{}:{}".format(*tim)
        zerd.append("{:<8}{}{}".format(temp, "." * worker(tim), temp))
    print(header)
    for lin in zerd:
        print(lin[:width])


if __name__ == "__main__":
    main()
