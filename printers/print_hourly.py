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


def print_hourly(hourly_wdb, sun_wdb, frmt='bars'):
    import printers.utilities
    width = printers.utilities.get_terminal_width()
    height = printers.utilities.get_terminal_height()
    COLORS = printers.utilities.get_colors(color_flag=True)
    if frmt == 'lines':
        import printers.ph_lines
        res = printers.ph_lines.hourly_by_lines(hourly_wdb, width, height)
    elif frmt == 'bars':
        import printers.ph_bars
        res = printers.ph_bars.hourly_by_bars(
            hourly_wdb, width, height,
            sun_wdb, COLORS,
            printers.utilities.sunrise_sunset_time)
    elif frmt == 'cols':
        import printers.ph_cols
        res = printers.ph_cols.hourly_by_cols(hourly_wdb, width, height,
                                              sun_wdb, COLORS,
                                              col_width=6)
    else:
        raise KeyError("print_hourly.print_hourly(...) passed bad format var")
        #  res = printers.ph_lines.hourly_by_lines(hourly_wdb, width, height)
    return res


def main():
    """ testing!
    """
    if '/usr/self/weather' not in sys.path:
        sys.path.append('/usr/self/weather/')
    import returner
    now = returner.main()
    print("Testing printing by lines:")
    nerd = print_hourly(now['hourly_forecast'], None, frmt='lines')
    for lin in nerd:
        print(lin)
    print("Testing bars...")
    zerd = print_hourly(now['hourly_forecast'], now['sun_phase'], frmt='bars')
    for lin in zerd:
        print(lin)
    print("Testing cols...")
    # COLORS = printers.utilities.get_colors(color_flag=True)
    # width = printers.utilities.get_terminal_width()
    # zing = list(z['temp']['english'] for z in now['hourly_forecast'])
    # nerd = cols_formatter(zing[:width//6], COLORS, bar_temp_color)
    gerd = print_hourly(now['hourly_forecast'], now['sun_phase'], frmt='cols')
    for lin in gerd:
        print(lin)


if __name__ == '__main__':
    main()
