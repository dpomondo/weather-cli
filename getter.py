#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#
#       CLI Weather reader & printer
#       author: dpomondo
#       purpose: avoid looking out the window
#
# -----------------------------------------------------------------------------
#
# TODO:     1. Add method for making daily database file -- DONE
#               a. include method for clearing out old files
#           2. add configuration file (ability to save preferred printing
#              format)
#           3. Add ASCII-art print method for temp etc. graph
#           4. add Curse display method
#           5. Separate:    a. single current conditions call
#                           b. hourly forecast call
#                           c. 10-day forecast call
#                           d. debugging call (keys, time, update, etc)
#           6. light-weight version for TMUX use
#           7. JSON explorer
#
# -----------------------------------------------------------------------------

import sys
# import os
import requests
import time
import json
import argparse
# kill the following:
import shelve


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='verbose flag'
                        )
    parser.add_argument('--keys', '-k',
                        action='store_true',
                        help='number of keys in database'
                        )
    parser.add_argument('--recent', '-r',
                        action='store_true',
                        help='time of most recent call'
                        )
    parser.add_argument('--query', '--requery', '-q',
                        action='store_true',
                        help='time until next re-query'
                        )
    parser.add_argument('--temperature', '-t',
                        action='store_true',
                        help='return current temperature in fahrenheit'
                        )
    parser.add_argument('--wind', '-w',
                        action='store_true',
                        help='return current wind speed and direction'
                        )
    parser.add_argument('--humidity', '-m',
                        action='store_true',
                        help='return current humidity'
                        )
    parser.add_argument('--conditions', '-c',
                        action='store_true',
                        help='return current conditions'
                        )
    parser.add_argument('--all', '-a',
                        action='store_true',
                        help='return temperature, wind, ' +
                        'humidity and sky conditions'
                        )
    parser.add_argument('--now', '-n',
                        action='store_true',
                        help='return conditions as they are now'
                        )
    parser.add_argument('--hourly', '-o',
                        action='store_true',
                        help='return hourly forecast'
                        )
    parser.add_argument('--forecast', '-f',
                        action='store_true',
                        help='return 10 day forecast'
                        )
    parser.add_argument('--update', '-u',
                        action='store_true',
                        help='force update of weather conditions database'
                        )
    parser.add_argument('--moon',
                        action='store_true',
                        help='return sunrise and sunset'
                        )
    parser.add_argument('--options', '-p',
                        action='store_true',
                        help='look at local options'
                        )
    parser.add_argument('--debug',
                        action='store_true',
                        help='print out current server response'
                        )

    return parser.parse_args()


def response_age():
    if 'current_response' in weather_db:
        res = (weather_db['current_response']
                         ['current_observation']
                         ['observation_epoch'])
        return int(time.time()) - int(res)
    else:
        ## without gloabl variables this line fails
        # return time_out + 1
        #
        ## this is a bad bad hacky thing
        return 601


def get_response(verbose=False, check_time=True, time_out=600, **kwargs):
    """ Fill the current_response object with the json returned
    from the website
    """
    import pprint
    if '/usr/self/weather' not in sys.path:
        sys.path.append('/usr/self/weather')
    import updater
    if verbose:
        print("Getting response from the server...")
    if time_out and check_time:
        if response_age() < time_out:
            if args.verbose:
                print("re-query too soon.")
                print("re-query possible in {} seconds".format(
                    time_out - response_age()))
            return
    params = kwargs.get('params', None)
    r = requests.get(updater.make_url(**kwargs), params=params)
    if sys.version_info[1] < 4:
        current_response = r.json
    else:
        current_response = r.json()
    if verbose:
        print('Response keys:')
        pprint.pprint(current_response.keys())
    return current_response


def update(weather_db, verbose=False, check_time=True):
    # do the thing
    # this is a very crummy emergency solution:
    home_dir = '/usr/self/weather/'
    config = home_dir + 'jwunderground.json'
    temp = load_vars(config=config)
    url = temp['url']
    req_keys = temp['req_keys']
    api = temp['api']
    time_out = int(temp.get('time_out', 600))

    import pprint
    now = get_response(verbose=verbose, check_time=check_time,
            time_out=time_out, **temp)
    # umm... the whole thing breaks if the server sends back the wrong thing?
    if now is not None and 'current_observation' in now:
        if verbose:
            print('Function returned this:')
            pprint.pprint(now.keys())
        weather_db['current_response'] = now
        weather_db[now['current_observation']['observation_epoch']] = now
        # for some reason, trying to dump `now['current_response']` to the json
        # file RECALLS this function, looping & crashing the whole thing
        nerd = {}
        for key in now:
            nerd[key] = now[key]
        with open(day_file_name() + ".json", "w") as outfile:
            json.dump(nerd, outfile, indent=2)
        del(nerd)
        if verbose:
            keys = list(weather_db.keys())
            print("weather_db has the following keys:")
            pprint.pprint(keys)


def key_printer(dic):
    key_color = '\033[38;5;214m'
    val_color = '\033[38;5;056m'
    end_color = '\033[0m'
    results = []
    new_len = 1
    for k in dic:
        if 1 + len(k) > new_len:
            new_len = len(k) + 1
    for key in sorted(dic.keys()):
        if isinstance(dic[key], dict):
            # remember kids: recursion is cool
            temp = key_printer(dic[key])
            results.append("{}{}:{:<{width}}{}".format(key_color, key, " ",
                    end_color, width=(new_len-len(key))))
            if len(temp) > 0:
                results[-1] += temp[0]
                for t in temp[1:]:
                    results.append((" " + " " * new_len) + t)
        else:
            results.append("{}{}:{:<{width}}{}{}{}".format(key_color, key, " ",
                val_color, dic[key], end_color, width=new_len-len(key)))
    return results


def print_current():
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
                                            weather_db['current_response']
                                                      ['current_observation']
                                                      [current_dic[key]['key']],
                                            color_clear,
                                            width=width - len(
                                                current_dic[key]['nam']) + 1))
    for lin in return_current:
        print(lin)


def print_moon():
    temp = []
    words = ["Moon Phase", "Sunrise", "Sunset"]
    words_max = max(list(len(z) for z in words))
    temp.append("{:>{width}}: {}".format(words[0],
        weather_db['current_response']['moon_phase']['phaseofMoon'],
        width=words_max))
    temp.append("{:>{width}}: {}:{}".format(words[1],
        weather_db['current_response']['moon_phase']['sunrise']['hour'],
        weather_db['current_response']['moon_phase']['sunrise']['minute'],
        width=words_max))
    temp.append("{:>{width}}: {}:{}".format(words[2],
        weather_db['current_response']['moon_phase']['sunset']['hour'],
        weather_db['current_response']['moon_phase']['sunset']['minute'],
        width=words_max))
    for lin in temp:
        print(lin)


def print_hourly():
    for hour in weather_db['current_response']['hourly_forecast'][0:13]:
        compound = "{:>9}, {:>2}:{:<2} {}".format(
            hour['FCTTIME']['weekday_name'],
            hour['FCTTIME']['hour'],
            hour['FCTTIME']['min'],
            hour['FCTTIME']['ampm'])
        print("{:>19}  temp:{:>4}\tconditions: {}".format(
            compound,
            hour['temp']['english'],
            hour['condition']))


def print_forecast():
    for day in (weather_db['current_response']
                          ['forecast']
                          ['simpleforecast']
                          ['forecastday']):
        print("{}, {} {}:\thigh of {}, low of {}, {}".format(
            day['date']['weekday'],
            day['date']['monthname'],
            day['date']['day'],
            day['high']['fahrenheit'],
            day['low']['fahrenheit'],
            day['conditions']))


def print_bookkeeping():
    # TODO: everything here should be returned via a call to updater:
    #           1. keys
    #           2. observation_epoch
    #           3. response age
    #       Add the following to updater:
    #           1. number_of_keys()
    #           2. latest_call()
    #           3. response_age()
    if args.keys:
        keys = list(weather_db.keys())
        print("number of keys: {}".format(len(keys)))
    if args.recent:
        print("Latest call: {}".format(
            time.ctime(float(weather_db['current_response']
                                       ['current_observation']
                                       ['observation_epoch']))))
    if args.query:
        print("re-query possible in {} seconds".format(
            # time_out - response_age()))
            600 - response_age()))


def load_vars(config):
    with open(config, 'r') as infile:
        temp = json.load(infile)
    return temp


def day_file_name():
    home_dir = '/usr/self/weather/'
    temp = home_dir + time.strftime("%d%b%y") + "_weather"
    return temp


if __name__ == '__main__':
    """ Hooray, a giant if-elif-else tree!
    """
    # TODO:     1. move ALL this junk to main(), call from here
    #           2. open shelve file here
    #           3. check to see if there IS a current response key
    #           4. put open/close shelve in update so it can be called
    #              seperately
    # -------------------------------------------------------------------------
    # init variables
    # -------------------------------------------------------------------------
    # shelve_file = '/usr/self/weather/june_weather'
    home_dir = '/usr/self/weather/'
    # shelve_file = home_dir + time.strftime("%d%b%y") + "_weather"
    config = home_dir + 'jwunderground.json'
    weather_db = shelve.open(day_file_name())

    loop_flag = True

    args = parse_arguments()

    while loop_flag is True:
        try:
            if args.update:
                args.verbose = True
                update(weather_db, verbose=args.verbose, check_time=True)
                loop_flag = False
            elif args.options:
                temp = load_vars(config)
                res = key_printer(temp)
                for r in res:
                    print(r)
                loop_flag = False
            elif args.debug:
                res = key_printer(weather_db['current_response']
                                            ['current_observation'])
                for r in res:
                    print(r)
                loop_flag = False
            elif args.moon:
                print_moon()
                loop_flag = False
            elif (args.keys or args.recent or args.query):
                print_bookkeeping()
                loop_flag = False
            elif args.now or not (args.hourly or args.forecast):
                print_current()
                loop_flag = False
            elif args.hourly:
                print_hourly()
                loop_flag = False
            elif args.forecast:
                print_forecast()
                loop_flag = False
            else:
                update(weather_db, verbose=args.verbose)
                loop_flag = False
        # here we'll put an `except` for key errors, but we'll need a way to:
        #       1. call the update() and...
        #       2. rerun the if/elif tree, which means...
        #       3 chopping down the elif tree!
        except KeyError:
            update(weather_db, verbose=args.verbose)
        finally:
            weather_db.close()
