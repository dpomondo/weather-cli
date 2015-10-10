#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#   file:   prinutils.py
#   use:    used for general formatting of lists etc. for printing
# -----------------------------------------------------------------------------


def new_cols_formatter(_l, COLOR, color_func, col_height=11, col_width=6):
    def indexer(_x):
        if col_height > 1 and diff > 0:
            return (col_height - 1) - int((_x - mn) / diff * (col_height - 1))
        else:
            return 0
    try:
        l = list(map(int, _l))
    except:
        try:
            l = list(map(float, _l))
        except:
            raise ValueError("""input list must be convertible to either int or
                             float""")
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
