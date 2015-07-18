#! /usr/local/bin/python3
# coding=utf-8

import json
import sys
import time

time_out = 600

home_dir = '/usr/self/weather/'
shelve_file = home_dir + time.strftime("%d%b%y") + "_weather"
with open(shelve_file + ".json", "r") as infile:
    current = json.load(infile)
# weather_db = shelve.open(shelve_file)

ob_ep = int(current['current_observation']['observation_epoch'])
if ob_ep + time_out < time.time():
    if '/usr/self/bin' not in sys.path:
        sys.path.append('/usr/self/bin')
    import shelve
    import getter
    weather_db = shelve.open(shelve_file)
    getter.update(weather_db, check_time=False)
    weather_db.close()
temp = current['current_observation']['temp_f']
# weather_db.close()
out = "Current Temp: {}".format(temp)

sys.stdout.write(out)
