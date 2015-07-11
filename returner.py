#! /usr/local/bin/python3
# coding=utf-8

import shelve
import sys
import time

time_out = 600

shelve_file = '/usr/self/weather/june_weather'
weather_db = shelve.open(shelve_file)

ob_ep = int(weather_db['current_response'][
    'current_observation']['observation_epoch'])
if ob_ep + time_out < time.time():
    if '/usr/self/bin' not in sys.path:
        sys.path.append('/usr/self/bin')
    weather_db.close()
    import getter
    getter.update()
    weather_db = shelve.open(shelve_file)
temp = weather_db['current_response']['current_observation']['temp_f']
weather_db.close()
out = "Current Temp: {}".format(temp)

sys.stdout.write(out)
