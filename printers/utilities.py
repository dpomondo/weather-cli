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
                  'precip100':  "\033[38;5;255m\033[48;5;232m"
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


def indexer_maker(start, header=0, col_width=6):
    """ returns a function to determine the index of an item.

        start:      start time, as a tuple: ("hour", "min")
        target:     item time, as a tuple
        header:     length of header
        col_width:  how wide each item will be in the final string
    start_hour, start_min = int(start[0]), int(start[1])
    """
    start_hour, start_min = int(start[0]), int(start[1])

    def index(hour, min, col_width):
        return hour * col_width + int(min // (60 / col_width))

    def maker(target):
        """ input: tuple (or list) -> ("hour", "min")
        """
        target_hour, target_min = int(target[0]), int(target[1])
        start_ind = index(start_hour, start_min, col_width)
        target_ind = index(target_hour, target_min, col_width)
        res = target_ind - start_ind
        if res >= 0:
            return header + res
        else:
            return header + target_ind + (index(24, 0, col_width) - start_ind)
    return maker


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
    #  heads = hours[r:] + hours[:r]
    heads = hours
    lis_len = (width - 8) // col_width
    header = " " * 8
    for tim in heads[:lis_len]:
        header = "{}{:>{wid}}".format(header, "{}:{}".format(tim, "00"),
                                      wid=col_width)
    nerd = []
    for i in range(10):
        nerd.append((random.choice(hours), random.choice(mins)))
    worker = indexer_maker((heads[0], "00"), header=8, col_width=col_width)
    zerd = []
    for tim in nerd:
        temp = "{}:{}".format(*tim)
        zerd.append("{:<8}{}{}".format(temp, "." * worker(tim), temp))
    print(header)
    for lin in zerd:
        print(lin[:width])


if __name__ == "__main__":
    main()
