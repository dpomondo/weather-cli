#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:   prinutils.py
#   use:    used for general formatting of lists etc. for printing
# -----------------------------------------------------------------------------


def indexer_maker(mn, mx, height):
    def indexer(_x):
        if _x is None:
            return None
        elif height > 1 and mx - mn > 0:
            return (height - 1) - int((_x - mn) / (mx - mn) * (height - 1))
        else:
            return 0
    return indexer


def dict_to_obj(dic):
    class Empty():
        pass
    temp = Empty()
    for key in dic:
        setattr(temp, key, dic[key])
    return temp


def clean_by_hours(obs, times, tups=True):
    """ takes a list index by hour, returns 24 averaged houlry observations.

        obs:    list of numbers (ints or floats)
        times:  list of datetimes
        tups:   False:  return a list of 24 averaged observations
                True:   return a list of 24 tuples with averaged observations
                        and time indexes
        """
    assert len(obs) == len(times), "clean_by_hours passed two unequal lists"
    import datetime as dt
    from collections import defaultdict
    hours, res = [], []
    collected = defaultdict(list)
    for i in range(24):
        hours.append(dt.time(hour=i))
    for ind in range(len(obs)):
        collected[dt.time(hour=times[ind].hour)].append(obs[ind])
    for h in hours:
        temp = len(collected[h])
        if temp == 0:
            res.append(None)
        elif temp == 1:
            res.append(collected[h][0])
        else:
            res.append(sum(collected[h]) / temp)
    if tups is True:
        return list(zip(res, hours))
    else:
        return res


def newer_cols_formatter(l, l2, start, func_obj, COLOR,
                         col_height=19, col_width=6):
    # important screen info!
    import sys
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import utils.utilities as utils
    screen_width = utils.get_terminal_width()
    screen_height = utils.get_terminal_height()

    # massage the func_obj into shape:
    if isinstance(func_obj, dict):
        func_obj = dict_to_obj(func_obj)
    func_obj_defaults = {'scale_format':        lambda x: str(x),
                         'right_string':        '| ',
                         'fargs':               [],
                         'label_fargs':         [],
                         'color_func':          '',
                         'label_color_func':    ''}
    for key in func_obj_defaults:
        if not hasattr(func_obj, key):
            setattr(func_obj, key, func_obj_defaults[key])

    if start is None:
        ind = 0
        while l[ind] is None:
            ind += 1
        start = l[ind]
    if hasattr(func_obj, 'scale_max') and hasattr(func_obj, 'scale_min'):
        mx = func_obj.scale_max(max(list(z for z in l if z is not None)))
        mn = func_obj.scale_min(min(list(z for z in l if z is not None)))
    else:
        mx = max(list(z for z in l if z is not None))
        mn = min(list(z for z in l if z is not None))

    col_height = min(col_height, screen_height - 4)
    if hasattr(func_obj, 'height_func'):
        old_col_height = col_height
        col_height = func_obj.height_func(mn, mx, col_height)
        if old_col_height != col_height:
            print("Changed {} to {}".format(old_col_height, col_height))

    zindexer = indexer_maker(mn, mx, col_height)
    # TODO:     get screen width and height (utils.get_terminal_width etc)
    #           limit l and l2 depending on col_width into screen width
    cols = column_maker(l[:((screen_width//col_width) - 2)],
                        start, zindexer, col_height, col_width,
                        func_obj, func_obj.color_func, COLOR)
    scale = scale_formatter(mx, mn, col_height, col_width,
                            func_obj.scale_format,
                            func_obj.right_string,
                            *func_obj.fargs)
    labels = func_obj.label_formatter(l2[:((screen_width//col_width) - 2)], 
                                      col_width,
                                      func_obj.label_func,
                                      func_obj.label_color_func,
                                      func_obj.label_test_func,
                                      COLOR,
                                      *func_obj.label_fargs)
    res = join_all(cols, scale, labels)
    return res


def new_cols_formatter(l, start, func_obj, color_func, COLOR,
                       col_height=11, col_width=6):
    """ formats a list of strings, based on an input list.

        func_obj:   either a dictioary or object with the following functions,
                    each of which take a member of list `l` and col-width as
                    arguments:
                    equal:      returns string for index == num
                    above:      returns string for index > num &&
                                                   index < start
                    below:      returns string for index > start
    """
    # convert a passed-in dict to a holder object
    if isinstance(func_obj, dict):
        func_obj = dict_to_obj(func_obj)

    if start is None:
        start = l[0]
    mx, mn = max(l), min(l)
    zindexer = indexer_maker(mn, mx, col_height)
    res = column_maker(l, start, zindexer, col_height, col_width,
                       func_obj, color_func, COLOR)
    return res, zindexer(start)


def column_maker(l, start, zindexer, col_height, col_width,
                 func_obj, color_func, COLOR):
    res = []
    if start is not None:
        start_index = zindexer(start)
    else:
        start_index = 0
    for i in range(col_height):
        res.append("")
    for num in l:
        if num is not None:
            ind = zindexer(num)
        else:
            ind = None
        for j in range(col_height):
            #  zing = ""
            if ind is None:
                zing = ('', ' ' * col_width, '')
            elif j == ind:
                zing = (color_func(num, start, COLOR),
                        func_obj.equal(num, col_width),
                        COLOR.clear)
            elif j > ind and j <= start_index:
                zing = (color_func(num, start, COLOR),
                        func_obj.above(num, col_width),
                        COLOR.clear)
            elif j < ind and j >= start_index:
                zing = (color_func(num, start, COLOR),
                        func_obj.below(num, col_width),
                        COLOR.clear)
            else:
                zing = (COLOR.clear,
                        "",
                        COLOR.clear)
            res[j] += "{}{:^{wid}}{}".format(*zing, wid=col_width)
    return res


def label_formatter(ll, col_width, format_func, color_func, test_func,
                    COLOR, skip=1, *fargs):
    checks, label = [], []
    width_test = format_func(ll[0], *fargs)
    while len(str(width_test)) > col_width * skip:
        skip += 1
    for ind in range(len(ll)):
        checks.append('{:-^{wid}}'.format('+', wid=col_width))
        temp = format_func(ll[ind], *fargs)
        if (ind + 1) % skip == 0:
            label.append('{}{:^{wid}}{}'.format(color_func(test_func, COLOR,
                                                           ind),
                                                #  str(temp)[:col_width],
                                                str(temp),
                                                COLOR.clear,
                                                wid=col_width * skip))
    res = []
    res.append(''.join(checks))
    res.append(''.join(label))
    return res


def multiline_label(ll, col_width, format_func, color_func, test_func,
                    COLOR, max_lines=4, *fargs):
    skip = 1
    formatted = []
    for i in range(len(ll)):
        formatted.append((color_func(test_func, COLOR, i),
                          format_func(ll[i], *fargs),
                          COLOR.clear))
    while len(formatted[0][1]) > col_width * skip:
        skip += 1
    if skip > max_lines:
        raise ValueError("Passed-in labels too long for formatting")
    # TODO: finish the function...


def scale_formatter(high, low, height, max_width, format_func=lambda x: str(x),
                    right_string=' | ', *fargs):
    distance = (high - low) / (height - 1)
    collected, res = [], []
    for ind in range(height):
        collected.append(format_func(high - (distance * ind), *fargs))
    for itm in collected:
        res.append("{:>{wid}}{}".format(str(itm), right_string, wid=max_width))
    return res


def single_column(num, target, func_obj, color_func, height, width):
    """ helper function
    """
    res = []
    for ind in range(height):
        if ind == num:
            res.append("{}{:^{wid}}{}".format(color_func(num, target, COLOR),
                                              func_obj.equal(num, width),
                                              COLOR.clear))
        elif ind > num:
            res.append("{}{:^{wid}}{}".format(color_func(num, target, COLOR),
                                              func_obj.above(num, width),
                                              COLOR.clear))
        else:
            res.append("{}{:^{wid}}{}".format(COLOR.clear,
                                              func_obj.below(num, width),
                                              COLOR.clear))
    return res


def join_all(cols, scale, labels):
    """ combines formatted lists into one list of lines.

        cols:       new-cols_formatter
        scale:      scale_formatter
        labels:     label_formatter
        """
    res = []
    for ind in range(len(cols)):
        res.append("{}{}".format(scale[ind], cols[ind]))
    for ind in range(len(labels)):
        res.append('{}{}'.format(' ' * len(scale[0]), labels[ind]))
    return res


def day_temps_formatter(temps, times):
    import sys
    import datetime as dt
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import utils.utilities as utils
    import printers.colorfuncs as cf
    width = utils.get_terminal_width()

    # make the passed-in objects
    col_width = min(5, width // 25)
    col_height = 21
    COLOR = utils.get_colors()

    def date_func(zed):
        if isinstance(zed, dt.datetime) or isinstance(zed, dt.time):
            temp = zed
        else:
            temp = dt.datetime.fromtimestamp(int(zed))
        return temp.strftime('%H:%M')

    def scale_min(x):
        return int(x - (x % 10))
        #  return int(x - (x % 5))

    def scale_max(x):
        #  return int(x + (10 - (x % 5)))
        return int(x + (10 - (x % 10)))

    def height_func(mn, mx, col_height):
        scales = [1, 2.5, 5, 10, 20]
        ind = 0
        while ind < len(scales) and (mx - mn) / scales[ind] > (col_height - 1):
            ind += 1
        return min(mx - mn // scales[ind - 1], col_height)

    funcs = {}
    funcs['above'] = lambda x, y: "{}{}{}".format(' ', '+' * (y - 2), ' ')
    funcs['equal'] = lambda x, y: str(x)[:y]
    funcs['below'] = lambda x, y: "{}{}{}".format(' ', '-' * (y - 2), ' ')
    funcs['color_func'] = cf.bar_temp_color
    funcs['label_func'] = date_func
    funcs['label_color_func'] = cf.new_alternating_bg
    funcs['label_test_func'] = lambda x: x % 2 == 0
    funcs['label_formatter'] = label_formatter
    funcs['scale_format'] = lambda x: str(round(x, 1))
    funcs['scale_max'] = scale_max
    funcs['scale_min'] = scale_min
    funcs['height_func'] = height_func

    # clean the input lists
    zepochs = list(map(lambda x: dt.datetime.fromtimestamp(int(x)), times))
    #  cleaned = clean_by_hours(opened[target_keys[0]], zepochs)
    cleaned = clean_by_hours(temps, zepochs)
    full = list(z[0] for z in cleaned)
    epochs = list(z[1] for z in cleaned)

    # call the wrapped func
    return newer_cols_formatter(full, epochs, None, funcs, COLOR,
                                col_height=col_height,
                                col_width=col_width)


def main(verbose=True):
    import sys
    import random
    #  import datetime as dt
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import utils.file_utils as fu
    #  import utils.utilities as utils
    #  import printers.colorfuncs as cf
    #  width = utils.get_terminal_width()

    # keys for parsing the random file
    target_keys = []
    target_keys.append(('current_observation', 'temp_f'))
    target_keys.append(('current_observation', 'observation_epoch'))

    # choose the random file
    fils = fu.list_dir(verbose)
    if verbose:
        print("{} files found...".format(len(fils)))
    target = random.choice(fils)
    if verbose:
        print("opening {}".format(target))
    opened = fu.parse_database(target, target_keys)

    res = day_temps_formatter(opened[target_keys[0]], opened[target_keys[1]])
    for lin in res:
        print(lin)


if __name__ == '__main__':
    main()
