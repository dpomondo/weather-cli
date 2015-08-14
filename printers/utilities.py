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


def get_colors(color_flag=True):
    """ Return object with color information.
    """
    class Colors:
        pass
    colors = Colors()
    if color_flag is False:
        color_info = {'temp':  '',
                      'wind':  '',
                      'high':  '',
                      'low':   '',
                      'cond':  '',
                      'clear': '',
                      'hot':   '',
                      'cool':  ''}
    else:
        color_info = {'temp':  "\033[1;34;47m",
                      'wind':  "\033[38;5;199m\033[48;5;157m",
                      'high':  "\033[1;34;47m",
                      'low':   "\033[1;34;47m",
                      'cond':  "\033[3;36;47m",
                      'clear': "\033[0m",
                      'hot':   "\033[38;5;160m\033[48;5;007m",
                      'cool':  "\033[38;5;020m\033[48;5;155m"}

    for key in color_info.keys():
        setattr(colors, key, color_info[key])
    return colors


def main():
    width = get_terminal_width()
    if width:
        print("{}: {}".format("width", width))

    height = get_terminal_height()
    if height:
        print("{}: {}".format("height", height))

if __name__ == "__main__":
    main()
