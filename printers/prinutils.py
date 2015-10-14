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


def main_old(verbose=True):
    import sys
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    import utils.file_utils as fu
    import utils.utilities as utils
    width = utils.get_terminal_width()
    import random
    funcs = {}
    funcs['above'] = lambda x, y: "+" * y
    funcs['equal'] = lambda x, y: str(x)[:y]
    funcs['below'] = lambda x, y: '-' * y
    # do the thing:
    COLOR = utils.get_colors()
    fils = fu.list_dir(verbose)
    if verbose:
        print("{} files found...".format(len(fils)))
    target = random.choice(fils)
    #  target = []
    #  target.append(random.choice(fils))
    if verbose:
        print("opening {}".format(target), end="")
    target_keys = []
    target_keys.append(('current_observation', 'temp_f'))
    opened = fu.parse_database(target, target_keys)
    #  parsed = opened[target_keys[0]][:width//4]
    full = opened[target_keys[0]]
    scale = scale_formatter(max(full), min(full), 20, 
                            format_func=lambda x: str(int(x)))
    parsed = full[:(width//4) - len(scale[0])]
    if verbose:
        print(", which has {} items".format(len(parsed)))
    start = 0 if random.random() < 0.5 else None
    res, st_ind = new_cols_formatter(parsed,
                                     start,
                                     funcs,
                                     lambda x, y, z: '',
                                     COLOR,
                                     col_height=20,
                                     col_width=4)
    assert len(res) == len(scale)
    for ind in range(len(res)):
        res[ind] = "{}{}".format(scale[ind], res[ind])
    for lin in res:
        print(lin)


def main():
    import sys
    home_dir = '/usr/self/weather/'
    if home_dir not in sys.path:
        sys.path.append(home_dir)
    #  import utils.file_utils as fu
    import utils.utilities as utils
    import random
    COLOR = utils.get_colors()
    funcs = {}
    funcs['above'] = lambda x, y: "+" * y
    funcs['equal'] = lambda x, y: str(x)[:y]
    funcs['below'] = lambda x, y: '-' * y

    parsed = []
    for i in range(20):
        parsed.append(str(random.random() * 100))
    start = 0 if random.random() < 0.5 else None
    res, st_ind = new_cols_formatter(parsed,
                                     start,
                                     funcs,
                                     lambda x, y, z: '',
                                     COLOR,
                                     col_height=20,
                                     col_width=4)
    for lin in res:
        print(lin)

if __name__ == '__main__':
    main_old()
