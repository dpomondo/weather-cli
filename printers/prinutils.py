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
        class Empty():
            pass
        temp = Empty()
        for key in func_obj:
            setattr(temp, key, func_obj[key])
        func_obj = temp
    #  res = []
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


def label_formatter(ll, col_width, format_func, color_func, COLOR, *fargs):
    checks, formatted = [], []
    test = lambda x: x % 2 == 0
    for ind in range(len(ll)):
        checks.append('{:-^{wid}}'.format('+', wid=col_width))
        temp = format_func(ll[ind], *fargs)
        formatted.append('{}{:^{wid}}{}'.format(color_func(test, COLOR, ind),
                                                str(temp)[:col_width],
                                                COLOR.clear,
                                                wid=col_width))
    res = []
    res.append(''.join(checks))
    res.append(''.join(formatted))
    return res


def wrapper_label(ll, col_width, format_func=lambda x: str(x), *fargs):
    return label_formatter(ll, col_width, format_func=lambda x: str(x), *fargs)


def scale_formatter(high, low, height, max_width, format_func=lambda x: str(x),
                    right_string=' | ', *fargs):
    distance = (high - low) / height
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
    funcs = {}
    funcs['above'] = lambda x, y: "{}{}{}".format(' ', '+' * (y - 2), ' ')
    funcs['equal'] = lambda x, y: str(x)[:y]
    funcs['below'] = lambda x, y: "{}{}{}".format(' ', '-' * (y - 2), ' ')
    target_keys = []
    target_keys.append(('current_observation', 'temp_f'))
    target_keys.append(('current_observation', 'observation_epoch'))
    COLOR = utils.get_colors()
    def date_func(zed):
        temp = dt.datetime.fromtimestamp(int(zed))
        return temp.strftime('%H:%M')

    # choose the random file
    fils = fu.list_dir(verbose)
    if verbose:
        print("{} files found...".format(len(fils)))
    target = random.choice(fils)
    if verbose:
        print("opening {}".format(target), end="")
    opened = fu.parse_database(target, target_keys)

    # start the parsing (this is the part that will get put into the wrapper
    # function)
    full = opened[target_keys[0]]
    scale = scale_formatter(max(full), min(full), col_height,
                            utils.max_len(map(str, full)),
                            format_func=lambda x: str(int(x)))
    #  parsed = full[:(width - len(scale[0]))//col_width]
    if verbose:
        print(", which has {} items".format(len(full)))
    start = 0 if random.random() < 0.5 else None
    #  start = None
    #  cols, st_ind = new_cols_formatter(parsed,
    cols, st_ind = new_cols_formatter(full[:((width//col_width) - 2)],
                                      start,
                                      funcs,
                                      #  lambda x, y, z: '',
                                      cf.bar_temp_color,
                                      COLOR,
                                      col_height=col_height,
                                      col_width=col_width)

    # make the labels
    epochs = opened[target_keys[1]]
    date_labels = label_formatter(epochs[:((width//col_width) - 2)],
    #  date_labels = label_formatter(epochs[:(width - len(scale[0]))//col_width],
                                  col_width, date_func,
                                  cf.new_alternating_bg, COLOR)

    # print the result
    res = join_all(cols, scale, date_labels)
    for lin in res:
        print(lin)


if __name__ == '__main__':
    main()
