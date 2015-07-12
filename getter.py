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
# TODO:     1. Add method for making daily database file
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
import requests
import time
import json
import shelve
# kill the following:
import pprint
import argparse

# shelve_file = '/usr/self/weather/june_weather'
home_dir = '/usr/self/weather/'
shelve_file = home_dir + time.strftime("%d%b%y") + "_weather"
config = home_dir + 'jwunderground.json'

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

args = parser.parse_args()

weather_db = shelve.open(shelve_file)

with open(config, 'r') as infile:
    temp = json.load(infile)

url = temp['url']
req_keys = temp['req_keys']
api = temp['api']
time_out = int(temp.get('time_out', 600))
params = temp.get('params', None)


def make_url():
    if not url.startswith('http://'):
        res = "{}{}".format("http://", url)
    else:
        res = url
    if req_keys.get('query', None):
        if req_keys.get('settings', None):
            res = "{}/api/{}/{}/{}/q/{}.{}".format(
                res,
                api,
                req_keys['features'],
                req_keys['settings'],
                req_keys['query'],
                req_keys['format']
                )
        else:
            res = "{}/api/{}/{}/q/{}.{}".format(
                res,
                api,
                req_keys['features'],
                req_keys['query'],
                req_keys['format']
                )
    return res


def response_age():
    if 'current_response' in weather_db:
        res = weather_db[
            'current_response']['current_observation']['observation_epoch']
        return int(time.time()) - int(res)
    else:
        return time_out + 1


def get_response():
    """ Fill the current_response object with the json returned
    from the website
    """
    if args.verbose:
        print("Getting response from the server...")
    if time_out:
        if response_age() < time_out:
            if args.verbose:
                print("re-query too soon.")
                print("re-query possible in {} seconds".format(
                    time_out - response_age()))
            return
    r = requests.get(make_url(), params=params)
    if sys.version_info[1] < 4:
        current_response = r.json
    else:
        current_response = r.json()
    if args.verbose:
        print('Response keys:')
        pprint.pprint(current_response.keys())
    return current_response


def update():
    # do the thing
    now = get_response()
    if now is not None:
        if args.verbose:
            print('Function returned this:')
            pprint.pprint(now.keys())
        weather_db['current_response'] = now
        weather_db[now['current_observation']['observation_epoch']] = now
        if args.verbose:
            keys = list(weather_db.keys())
            print("weather_db has the following keys:")
            pprint.pprint(keys)


def print_current():
    if args.all:
        args.temperature = True
        args.wind = True
        args.humidity = True
        args.conditions = True
    if args.temperature or not (args.wind or
                                args.humidity or
                                args.conditions):
        print("Temp: {}".format(weather_db['current_response']
                                          ['current_observation']
                                          ['temp_f']))
    if args.wind:
        print("Wind: {}".format(weather_db['current_response']
                                          ['current_observation']
                                          ['wind_string']))
    if args.humidity:
        print("Relative Humidity: {}".format(
            weather_db['current_response']
            ['current_observation']
            ['relative_humidity']))
    if args.conditions:
        print("Sky: {}".format(weather_db['current_response']
                                         ['current_observation']
                                         ['weather']))


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
            time_out - response_age()))

if __name__ == '__main__':
    """ Hooray, a giant if-elif-else tree!
    """
    try:
        if args.update:
            args.verbose = True
            update()
        elif (args.keys or args.recent or args.query):
            print_bookkeeping()
        elif args.now or not (args.hourly or args.forecast):
            print_current()
        elif args.hourly:
            print_hourly()
        elif args.forecast:
            print_forecast()
        else:
            update()
    # here we'll put an `except` for key errors, but we'll need a way to:
    #       1. call the update() and...
    #       2. rerun the if/elif tree, which means...
    #       3 chopping down the elif tree!
    # except:
    finally:
        weather_db.close()
