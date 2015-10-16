#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:   prinutils.py
#   use:    used for general formatting of lists etc. for printing
# -----------------------------------------------------------------------------


def indexer(_x, mn, diff, col_height):
    if col_height > 1 and diff > 0:
        return (col_height - 1) - int((_x - mn) / diff * (col_height - 1))
    else:
        return 0


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
    diff = mx - mn
    res = column_maker(l, start, mn, diff, col_height, col_width,
                       func_obj, color_func, COLOR)
    #  print("min: {} max: {} diff: {}".format(mn, mx, diff))
    return res, indexer(start, mn, diff, col_height)


def column_maker(l, start, mn, diff, col_height, col_width,
                 func_obj, color_func, COLOR):
    res = []
    star_index = indexer(start, mn, diff, col_height)
    for i in range(col_height):
        res.append("")
    for num in l:
        ind = indexer(num, mn, diff, col_height)
        for j in range(col_height):
            zing = ""
            if j == ind:
                zing = (color_func(num, start, COLOR),
                        func_obj.equal(num, col_width),
                        COLOR.clear)
            elif j > ind and j <= star_index:
                zing = (color_func(num, start, COLOR),
                        func_obj.above(num, col_width),
                        COLOR.clear)
            elif j < ind and j >= star_index:
                zing = (color_func(num, start, COLOR),
                        func_obj.below(num, col_width),
                        COLOR.clear)
            else:
                zing = (COLOR.clear,
                        "",
                        COLOR.clear)
            res[j] += "{}{:^{wid}}{}".format(*zing, wid=col_width)
    return res


#  def label_formatter(ll, col_width, format_func=lambda x: str(x), *fargs):
def label_formatter(ll, col_width, format_func, *fargs):
    checks, formatted = [], []
    for itm in ll:
        checks.append('{:-^{wid}}'.format('+', wid=col_width))
        temp = format_func(itm, *fargs)
        formatted.append('{:^{wid}}'.format(str(temp)[:col_width],
                                            wid=col_width))
    res = []
    res.append(''.join(checks))
    res.append(''.join(formatted))
    return res


def wrapper_label(ll, col_width, format_func=lambda x: str(x), *fargs):
    return label_formatter(ll, col_width, format_func=lambda x: str(x), *fargs)


def scale_formatter(high, low, height, format_func=lambda x: str(x),
                    right_string=' | ', *fargs):
    import sys
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import utils.utilities as utils
    distance = (high - low) / height
    collected, res = [], []
    for ind in range(height):
        collected.append(format_func(high - (distance * ind), *fargs))
    longest = utils.max_len(collected)
    for itm in collected:
        res.append("{:>{wid}}{}".format(str(itm), right_string, wid=longest))
    return res


def new_column_maker(l, start, mn, diff, col_height, col_width,
                     func_obj, color_func, COLOR):
    res = []
    for num in l:
        pass


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
    width = utils.get_terminal_width()

    # make the passed-in objects
    col_width=6
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
                            format_func=lambda x: str(int(x)))
    parsed = full[:(width - len(scale[0]))//col_width]
    if verbose:
        print(", which has {} items".format(len(parsed)))
    start = 0 if random.random() < 0.5 else None
    cols, st_ind = new_cols_formatter(parsed,
                                     start,
                                     funcs,
                                     lambda x, y, z: '',
                                     COLOR,
                                     col_height=col_height,
                                     col_width=col_width)

    # make the labels
    epochs = opened[target_keys[1]]
    date_labels = label_formatter(epochs[:(width - len(scale[0]))//col_width],
                                  col_width, date_func)

    # print the result
    res = join_all(cols, scale, date_labels)
    for lin in res:
        print(lin)


if __name__ == '__main__':
    main()
