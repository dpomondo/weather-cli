#! /usr/local/bin/python3
# coding=utf-8
#
# -----------------------------------------------------------------------------
#       file:       moon.py
#     author:       dpomondo
#       deps:       called from getter.py
# -----------------------------------------------------------------------------


def print_moon(weat_db):
    temp = []
    words = ["Moon Phase", "Sunrise", "Sunset"]
    words_max = max(list(len(z) for z in words))
    temp.append("{:>{width}}: {}".format(words[0],
                                         weat_db['phaseofMoon'],
                                         width=words_max))
    temp.append("{:>{width}}: {}:{}".format(words[1],
                                            weat_db['sunrise']['hour'],
                                            weat_db['sunrise']['minute'],
                                            width=words_max))
    temp.append("{:>{width}}: {}:{}".format(words[2],
                                            weat_db['sunset']['hour'],
                                            weat_db['sunset']['minute'],
                                            width=words_max))
    for lin in temp:
        print(lin)
