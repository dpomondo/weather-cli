#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:   prinutils.py
#   use:    used for general formatting of lists etc. for printing
# -----------------------------------------------------------------------------


def indexer_maker(mn, mx, height):
    def indexer(_x):
        if height > 1 and mx - mn > 0:
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
        start = l[0]
    if hasattr(func_obj, 'scale_max') and hasattr(func_obj, 'scale_min'):
        mx = func_obj.scale_max(max(l))
        mn = func_obj.scale_min(min(l))
    else:
        mx, mn = max(l), min(l)
    zindexer = indexer_maker(mn, mx, col_height)
    #TODO: get screen width and height (utils.get_terminal_width etc)
    #      limit l and l2 depending on col_width into screen width
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
    start_index = zindexer(start)
    for i in range(col_height):
        res.append("")
    for num in l:
        ind = zindexer(num)
        for j in range(col_height):
            #  zing = ""
            if j == ind:
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
    checks, formatted = [], []
    #  test = lambda x: x % 2 == 0
    width_test = format_func(ll[0], *fargs)
    while len(str(width_test)) > col_width * skip:
        skip += 1
    for ind in range(len(ll)):
        checks.append('{:-^{wid}}'.format('+', wid=col_width))
        temp = format_func(ll[ind], *fargs)
        if (ind + 1) % skip == 0:
            formatted.append('{}{:^{wid}}{}'.format(color_func(test_func, COLOR,
                                                               ind),
                                                    #  str(temp)[:col_width],
                                                    str(temp),
                                                    COLOR.clear,
                                                    wid=col_width * skip))
    res = []
    res.append(''.join(checks))
    res.append(''.join(formatted))
    return res


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
        #  date_labels[ind] = '{}{}'.format(' ' * len(scale[0]), date_labels[ind])
        res.append('{}{}'.format(' ' * len(scale[0]), labels[ind]))
    return res

def main(verbose=True):
    import sys
    import random
    import datetime as dt
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import utils.file_utils as fu
    import utils.utilities as utils
    import printers.colorfuncs as cf
    width = utils.get_terminal_width()

    # make the passed-in objects
    col_width=5
    col_height=20
    COLOR = utils.get_colors()
    target_keys = []
    target_keys.append(('current_observation', 'temp_f'))
    target_keys.append(('current_observation', 'observation_epoch'))
    def date_func(zed):
        temp = dt.datetime.fromtimestamp(int(zed))
        return temp.strftime('%H:%M')
    def scale_min(x):
        return int(x - (x % 10))
    def scale_max(x):
        return int(x + (10 - (x % 10)))
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

    # choose the random file
    fils = fu.list_dir(verbose)
    if verbose:
        print("{} files found...".format(len(fils)))
    target = random.choice(fils)
    if verbose:
        print("opening {}".format(target), end="")
    opened = fu.parse_database(target, target_keys)

    full = opened[target_keys[0]]
    epochs = opened[target_keys[1]]
    start = 0 if random.random() < 0.5 else None
    res = newer_cols_formatter(full, epochs, start, funcs, COLOR,
                               col_height=col_height,
                               col_width=col_width)
    if verbose:
        print(", which has {} items".format(len(full)))
    for lin in res:
        print(lin)


if __name__ == '__main__':
    main()
