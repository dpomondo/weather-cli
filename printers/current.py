#! /usr/local/bin/python3
# coding=utf-8

# -----------------------------------------------------------------------------
#
#         file:     current.py
#       author:     dpomondo
# dependencies:     imported and called from getter.py
#
# -----------------------------------------------------------------------------


def print_current(weather_db, args):
    return_current = []
    temp_colors = ";".join([str(1), str(34), str(47)])
    color_code = "\033[{}m".format(temp_colors)
    color_clear = "\033[0m"
    current_dic = {"1Temp":  {'arg': 'temperature',
                              'nam': "Temp",
                              'key': 'temp_f',
                              'col': "\033[1;34;47m"},
                   "2Wind":  {'arg': 'wind',
                              'nam': "Wind",
                              'key': 'wind_string',
                              'col': "\033[38;5;199m\033[48;5;157m"},
                   "3Relative Humidity":
                             {'arg': 'humidity',
                              'nam': "Humidity",
                              'key': 'relative_humidity',
                              'col': "\033[2;34m"},
                   "4Sky":   {'arg': 'conditions',
                              'nam': "Conditions",
                              'key': 'weather',
                              'col': '\033[3;36;47m'}
                   }
    # make sure SOMETHING gets printed:
    if not (args.wind or
            args.humidity or
            args.conditions or
            args.temperature or
            args.all):
        args.temperature = True
    if args.all:
        args.temperature = True
        args.wind = True
        args.humidity = True
        args.conditions = True
    _lis = []
    for k in current_dic:
        if getattr(args, current_dic[k]['arg']) is True:
            _lis.append(k)
    _lis.sort()
    # debug line!
    if args.debug:
        print("list of keys to print: " + str(_lis))
    width = max(list(len(item) for item in list(current_dic[k]['nam'] for k in
        _lis)))
    # print("width:\t" + str(width), type(width))

    # and below here is what's getting changed up:
    for key in _lis:
        color_code = current_dic[key]['col']
        return_current.append("{}:{}{:<{width}}{}{}".format(
                                            current_dic[key]['nam'],
                                            color_code,
                                            " ",
                                            weather_db[current_dic[key]['key']],
                                            color_clear,
                                            width=width - len(
                                                current_dic[key]['nam']) + 1))
    # print the thing!
    for lin in return_current:
        print(lin)
