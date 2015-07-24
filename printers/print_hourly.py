#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#       file:   print_hourly.py
#     author:   dpomondo
#
#               Called form getter.py
# -----------------------------------------------------------------------------

import subprocess


def get_terminal_info(arg):
    """ does what it says: returns terminal width as an int.

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


def print_hourly(weather_db):
    for hour in weather_db:
        compound = "{:>9}, {:>2}:{:<2}".format(
            hour['FCTTIME']['weekday_name'],
            hour['FCTTIME']['hour'],
            hour['FCTTIME']['min'])
        print("{:>16}  temp:{:>4}\tconditions: {}".format(
            compound,
            hour['temp']['english'],
            hour['condition']))


def main():
    width = get_terminal_width()
    if width:
        print("{}: {}".format("width", width))

    height = get_terminal_height()
    if height:
        print("{}: {}".format("height", height))

if __name__ == "__main__":
    main()
