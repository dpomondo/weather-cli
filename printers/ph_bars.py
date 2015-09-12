import sys
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import utils.utilities
import printers.colorfuncs as cf


def format_bar(color_func, target, curr, COLOR, width):
    """ returns a formatted string with color escape codes
    """
    return "{}{:^{wid}}{}".format(color_func(target, curr, COLOR),
                                  target, COLOR.clear, wid=width)


def format_bar_hour(weat_hour, COLOR, zero_hour, sunrise, sunset, sun_func,
                    time_func):
    """ return a vertical set of strings, one hour of info
    """
    res = []
    for r in [(('temp', 'english'), cf.bar_temp_color),
              (('sky', ), cf.bar_cloud_color),
              (('pop', ), cf.bar_precip_color),
              (('wspd', 'english'), cf.bar_wind_color)]:
        target = utils.utilities.eat_keys(weat_hour, r[0])
        currs = utils.utilities.eat_keys(zero_hour, r[0])
        res.append(format_bar(r[1], int(target), int(currs), COLOR, width=6))
    # TODO: if sunrise_sunset_color can get wrangled into the standard
    # color_func api, we can move this to a format_bar call:
    res.append("{}{:^6}{}".format(
        cf.sunrise_sunset_color(weat_hour['FCTTIME']['hour'],
                                sunrise, sunset, COLOR),
        sun_func(weat_hour['FCTTIME']['hour'], sunrise, sunset),
        COLOR.clear))
    #  res.append("{:^6}".format("{}:{}".format(weat_hour['FCTTIME']['hour'],
                                             #  weat_hour['FCTTIME']['min'])))
    res.append(next(time_func))
    return res


def hourly_by_bars(hourly_wdb, width, height, sun_wdb, COLORS, sun_func,
                   col_width=6):
    """ for each hour, return a vertical set of strings with the formatted info
    """
    res = [[]]
    fins = []
    _keys = ["Temp", "Cloud %", "Precip Chance", "Wind speed",
             "Sunrise/set", "Time"]
    head = utils.utilities.max_len(_keys)
    time_line = phutils.utilities.time_format_generator(hourly_wdb,
                                                             "Time", head,
                                                             col_width)
    # generator spits out a header, lets send it into space:
    _ = next(time_line)
    del(_)
    for k in _keys:
        res[0].append("{:>{width}}: ".format(k, width=head))
    # for i in range((width - max(list(len(z) for z in res[0])))//6):
    for i in range((width - len(res[0][0])) // col_width):
        res.append(format_bar_hour(hourly_wdb[i], COLORS, hourly_wdb[0],
                   (sun_wdb['sunrise']['hour'], sun_wdb['sunrise']['minute']),
                   (sun_wdb['sunset']['hour'], sun_wdb['sunset']['minute']),
                   sun_func, time_line))
    for i in range(len(res[0])):
        fins.append(''.join(z[i] for z in res))
    return fins
