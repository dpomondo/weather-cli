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


def new_eat_keys(_lis, _keys):
    from functools import reduce
    temp = []
    temp.append(_lis)
    temp += _keys
    return reduce(lambda x, y: x[y], temp)


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


def main():
    # test width func
    width = get_terminal_width()
    if width:
        print("{}: {}".format("width", width))

    # test height func
    height = get_terminal_height()
    if height:
        print("{}: {}".format("height", height))

    # test eat_keys
    def key_adder(_dic, iters, max_iters):
        def word_maker():
            temp = ""
            for i in range(3):
                temp += random.choice(woodpile)
            return temp
        # begin key_adder func proper...
        #  curr_its = iters
        nums = random.randint(2, 5)
        for i in range(nums):
            temp = word_maker()
            if iters >= max_iters or (iters > 1 and random.random() < 0.2):
                _dic[temp] = word_maker()
            else:
                new_dic = {}
                key_adder(new_dic, iters + 1, max_iters)
                _dic[temp] = new_dic
        return

    def target_maker(_dic):
        target = []
        zemp = verklemp
        while isinstance(zemp, dict):
            rands = random.choice(list(zemp.keys()))
            target.append(rands)
            zemp = zemp[rands]
        return target

    def sum_dic(_dic):
        total = 0
        for key in _dic:
            if isinstance(_dic[key], dict):
                total += sum_dic(_dic[key])
            else:
                total += 1
        return total

    import random
    import string
    import sys
    home_dir = '/usr/self/weather'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import config.loaders
    woodpile = list(string.ascii_letters)
    verklemp = {}

    key_adder(verklemp, 0, 4)
    print("Testing eat_keys function...")
    print("Eating the keys in the following:")
    #  res = config.loaders.key_formatter(verklemp)
    #  for lin in res:
        #  print(lin)
    print("Test dictionary contains {} items...".format(sum_dic(verklemp)))
    for i in range(3):
        target = target_maker(verklemp)
        print("Testing the following sequence: {}".format(str(target)))
        basket = verklemp
        for t in target:
            basket = basket[t]
        ball = eat_keys(verklemp, target)
        potato = new_eat_keys(verklemp, target)
        print("{:<20}: {}".format("Iterating over keys", basket))
        print("{:<20}: {}".format("Function call", ball))
        print("{:<20}: {}".format("Reduce + lambda", potato))


if __name__ == "__main__":
    main()
