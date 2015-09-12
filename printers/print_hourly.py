#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#       file:   print_hourly.py
#     author:   dpomondo
#
#               Called form getter.py
# -----------------------------------------------------------------------------

import sys
#  import math
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
#  import printers.colorfuncs as cf


def print_hourly(hourly_wdb, sun_wdb, configs):
    import utils.utilities
    width = utils.utilities.get_terminal_width()
    height = utils.utilities.get_terminal_height()
    COLORS = utils.utilities.get_colors(color_flag=True)
    if configs.print_hourly == 'lines':
        import printers.ph_lines
        res = printers.ph_lines.hourly_by_lines(hourly_wdb, width, height)
    elif configs.print_hourly == 'bars':
        import printers.phutils as phutils
        import printers.ph_bars
        res = printers.ph_bars.hourly_by_bars(
            hourly_wdb, width, height,
            sun_wdb, COLORS,
            phutils.sunrise_sunset_time)
    elif configs.print_hourly == 'cols':
        import printers.ph_cols as ph_cols
        res = ph_cols.hourly_by_cols(hourly_wdb, width, height,
                                     sun_wdb, COLORS,
                                     col_width=6)
    else:
        message = "print_hourly function passed bad format var: {}".format(
            configs.print_hourly)
        raise KeyError(message)
        #  res = printers.ph_lines.hourly_by_lines(hourly_wdb, width, height)
    return res


def main():
    """ testing!
    """
    if '/usr/self/weather' not in sys.path:
        sys.path.append('/usr/self/weather/')
    import config.loaders
    import returner
    now = returner.main()
    temp_config = config.loaders.parse_config()
    print("Testing printing by lines:")
    temp_config.print_hourly = 'lines'
    nerd = print_hourly(now['hourly_forecast'], None, temp_config)
    for lin in nerd:
        print(lin)
    print("Testing bars...")
    temp_config.print_hourly = 'bars'
    zerd = print_hourly(now['hourly_forecast'], now['sun_phase'], temp_config)
    for lin in zerd:
        print(lin)
    print("Testing cols...")
    temp_config.print_hourly = 'cols'
    # COLORS = utils.utilities.get_colors(color_flag=True)
    # width = utils.utilities.get_terminal_width()
    # zing = list(z['temp']['english'] for z in now['hourly_forecast'])
    # nerd = cols_formatter(zing[:width//6], COLORS, bar_temp_color)
    gerd = print_hourly(now['hourly_forecast'], now['sun_phase'], temp_config)
    for lin in gerd:
        print(lin)


if __name__ == '__main__':
    main()
