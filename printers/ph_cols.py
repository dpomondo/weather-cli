import sys
if '/usr/self/weather' not in sys.path:
    sys.path.append('/usr/self/weather/')
import utils.utilities as utils
import printers.phutils as phutils
import printers.colorfuncs as cf


def cols_formatter(_l, COLOR, color_func, col_height=11, col_width=6):
    def indexer(_x):
        # return height - math.floor((_x - mn) / diff * height)
        # return (height - 1) - math.floor((_x - mn) / diff * (height - 1))
        # return (height - 1) - math.ceil((_x - mn) / diff * (height - 1))
        # return (height - 1) - round((_x - mn) / diff * (height - 1))
        if col_height > 1 and diff > 0:
            return (col_height - 1) - int((_x - mn) / diff * (col_height - 1))
        else:
            return 0
    l = list(map(int, _l))
    res = []
    start = l[0]
    mx = max(l)
    mn = min(l)
    diff = mx - mn
    #  rng = diff / height
    #  print("min: {} max: {} diff: {}".format(mn, mx, diff))
    for i in range(col_height):
        res.append("")
    star_index = indexer(start)
    for num in l:
        index = indexer(num)
        for j in range(col_height):
            zing = ""
            if j == index:
                zing = color_func(num, start, COLOR), num, COLOR.clear
            elif j > index and j <= star_index:
                zing = color_func(num, start, COLOR), "++", COLOR.clear
            elif j < index and j >= star_index:
                zing = color_func(num, start, COLOR), "--", COLOR.clear
            else:
                zing = COLOR.clear, "", COLOR.clear
            res[j] += "{}{:^{wid}}{}".format(*zing, wid=col_width)
    return res, star_index


def new_hourly_by_cols():
    """ inputs:
        format_dict ->  specifies the order in which data functions get
                        called.
                        form:
                            {1: "Temp",
                                2: "Cloud Cover"... etc}
                        use:
                        for n in range(len(format_dict)):
                            function_dict[format_dict[n]]
        function_dict -> specifies the function and parameters for each
                        data function call.
                        form:
                            {"Temp": (temp_func, [db, color_func...]),
                            {"Cloud Cover": (cloud_func, db, [...]),
                                etc... }
                        use:
                            function_dict["xxx"][0](*function_dict["xxx"](1))
                        example:
                            "Temp": (cols_formater, [_lis[:ind_slice], ...])

    """
    pass


def hourly_by_cols(hourly_wdb, width, height, sun_wdb, COLORS, col_width=5):
    """ for each bit of info, format the entire horizontal string at once

        And yes, that means `hourly_by_cols` and `hourly_by_bars` are named
        exactly backwards...
    """
    # this does not belong here. Need to figure oout how to kill it...
    #  import utils.utilities as utils
    #  import printers.colorfuncs as cf
    # begin main functioning!
    res = []
    _keys = ["Temp", "Cloud %", "Precip Chance", "Wind speed",
             "Sunrise/set", "Time"]
    head = max(list(len(z) for z in _keys))
    ind_slice = (width - head - 2) // col_width
    # build the basic info strings
    # NOTE: fix the mix of tuples and lists...
    format_table = [["Temp", ('temp', 'english'), cf.bar_temp_color, 11],
                    ("Cloud %", ('sky', ), cf.bar_cloud_color, 1),
                    ("Precip Chance", ('pop', ), cf.bar_precip_color, 1),
                    ("Wind speed", ('wspd', 'english'), cf.bar_wind_color, 1)]
    # here we make sure we don't return something higher tha=n the screen
    #   NOTE:
    #   the magic '3' will disappear once the whole format_table gets built
    #   according to a formatting function
    table_height = sum(list(f[3] for f in format_table)) + 3
    if table_height > height:
        format_table[0][3] = max(1, format_table[0][3] - (table_height
                                 - height))
    for r in format_table:
        _lis = list(utils.eat_keys(
            hour, r[1]) for hour in hourly_wdb)
        temp, star_ind = cols_formatter(_lis[:ind_slice],
                                        COLORS, r[2], r[3], col_width)
        for lin in range(len(temp)):
            res.append("{}{}".format("{:>{wid}}{}".format(r[0], ": ", wid=head)
                       if lin == star_ind else " " * (head + 2), temp[lin]))
    # build the sunrise/sunset string
    # build the alternate sunrise/sunset string
    temp = phutils.new_sunrise_line(hourly_wdb[:ind_slice], sun_wdb, COLORS,
                                    col_width=col_width, head=head)
    res.append(temp)
    # build the time string
    # TEST 1
    #  sunrise = (sun_wdb['sunrise']['hour'], sun_wdb['sunrise']['minute'])
    #  sunset = (sun_wdb['sunrise']['hour'], sun_wdb['sunrise']['minute'])
    #  color_func = cf.sunrise_sunset_color
    #  color_func_vars = [sunrise, sunset, COLORS]
    #  TEST 2
    #  color_func = cf.new_sunrise_sunset_color
    #  color_func_vars = [sunrise, sunset, COLORS]
    #  TEST 3
    color_func = cf.alternating_background
    color_func_vars = [lambda x, y: x % 2 == 1, COLORS]
    #  TEST 3 1/2
    #  color_func_vars = [lambda x, y: x < 10, COLORS]
    temp = "".join(list(phutils.time_format_generator(hourly_wdb[:ind_slice],
                                                      "Time", head,
                                                      col_width,
                                                      color_func, COLORS.clear,
                                                      *color_func_vars)))
    # build the alternate time string
    res.append(temp)
    #  insert a line before and after? No... let's not
    #  res.insert(0, '-' * (head + col_width * ind_slice))
    #  res.append('-' * (head + col_width * ind_slice))
    # return the result!
    return res
