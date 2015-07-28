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
import os
import time
import json
import argparse
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
    parser.add_argument('--times', '-i',
                        action='store_true',
                        help='list all times of todays server queries'
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


def response_age(db_file):
    if 'current_observation' in db_file:
        res = db_file['current_observation']['observation_epoch']
        return int(time.time()) - int(res)
    else:
        # without gloabl variables this line fails
        # return time_out + 1
        #
        # this is a bad bad hacky thing
        return 601


def update(weather_db, verbose=False, check_time=True):
    # do the thing
    # this is a very crummy emergency solution:
    home_dir = '/usr/self/weather'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import config.loaders
    config_file = os.path.join(home_dir,  'config',  'jwunderground.json')
    temp = config.loaders.load_vars(config_file=config_file)
    time_out = int(temp.get('time_out', 600))
    weat_db_file = shelve.open(weather_db)

    if check_time and 'currernt_response' in weat_db_file:
        if response_age(weat_db_file['current_response']) < time_out:
            if args.verbose:
                print("re-query too soon.")
                print("re-query possible in {} seconds".format(
                    time_out - response_age()))
            return
    import updater
    now = updater.get_response(verbose=verbose, **temp)
    # umm... the whole thing breaks if the server sends back the wrong thing?
    if now is not None and 'current_observation' in now:
        if verbose:
            import pprint
            print('Function returned this:')
            pprint.pprint(now.keys())
        weat_db_file['current_response'] = now
        weat_db_file[now['current_observation']['observation_epoch']] = now
        weat_db_file.close()
        # for some reason, trying to dump `now['current_response']` to the json
        # file RECALLS this function, looping & crashing the whole thing
        nerd = {}
        for key in now:
            nerd[key] = now[key]
        import config.loaders
        with open(config.loaders.day_file_name() + ".json", "w") as outfile:
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
            results.append("{}{}:{:<{width}}{}".format(key_color,
                                                       key,
                                                       " ",
                                                       end_color,
                                                       width=(new_len-len(key))
                                                       ))
            if len(temp) > 0:
                results[-1] += temp[0]
                for t in temp[1:]:
                    results.append((" " + " " * new_len) + t)
        else:
            results.append("{}{}:{:<{width}}{}{}{}".format(key_color,
                                                           key,
                                                           " ",
                                                           val_color,
                                                           dic[key],
                                                           end_color,
                                                           width=new_len-len(
                                                               key)))
    return results


def print_bookkeeping(current_ob, weat_db):
    # TODO: everything here should be returned via a call to updater:
    #           1. keys
    #           2. observation_epoch
    #           3. response age
    #       Add the following to updater:
    #           1. number_of_keys()
    #           2. latest_call()
    #           3. response_age()
    if args.times or args.keys:
        import updater
        keys = updater.list_keys(weat_db)
    if args.times:
        for k in keys[:-1]:     # cut off 'current_response' key
            print('{}: {}'.format(k, time.ctime(int(k))))
    if args.keys:
        print("number of keys: {}".format(len(keys)))
    if args.recent:
        print("Latest call: {}".format(
            time.ctime(float(current['current_observation']
                                    ['observation_epoch']))))
    if args.query:
        print("re-query possible in {} seconds".format(
            # time_out - response_age()))
            600 - response_age(current_ob)))


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
    home_dir = '/usr/self/weather'
    config_file = os.path.join(home_dir, 'config', 'jwunderground.json')
    # here we make sure the package imports can go through:
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import config.loaders
    import returner
    weather_db = config.loaders.day_file_name()
    current = returner.main()

    args = parse_arguments()
    loop_flag = True
    while loop_flag is True:
        try:
            if args.update:
                args.verbose = True
                update(weather_db, verbose=args.verbose, check_time=True)
                loop_flag = False
            elif args.options:
                # import config.loaders
                temp = config.loaders.load_vars(config_file)
                res = key_printer(temp)
                for r in res:
                    print(r)
                loop_flag = False
            elif args.debug:
                res = key_printer(current['current_observation'])
                for r in res:
                    print(r)
                loop_flag = False
            elif args.moon:
                import printers.moon
                printers.moon.print_moon(current['moon_phase'])
                loop_flag = False
            elif (args.keys or args.recent or args.query or args.times):
                print_bookkeeping(current_ob=current, weat_db=weather_db)
                loop_flag = False
            elif args.now or not (args.hourly or args.forecast):
                import printers.current
                printers.current.print_current(current['current_observation'],
                                               args)
                loop_flag = False
            elif args.hourly:
                import printers.print_hourly
                printers.print_hourly.print_hourly(current['hourly_forecast']
                                                          [0:13])
                loop_flag = False
            elif args.forecast:
                import printers.forecast
                printers.forecast.print_forecast(current['forecast']
                                                        ['simpleforecast']
                                                        ['forecastday'])
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
        # finally:
            # weather_db.close()
