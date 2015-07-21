#! /usr/local/bin/python3
# coding=utf-8

# -----------------------------------------------------------------------------
#         file:     updater.py
#       author:     dpomondo
# dependencies:     imported and called from getter.py, returner.py
#
# -----------------------------------------------------------------------------


def make_url(**temp):
    url = temp['url']
    req_keys = temp['req_keys']
    api = temp['api']
    if not url.startswith('http://'):
        res = "{}{}".format("http://", url)
    else:
        res = url
    if req_keys.get('query', None):
        if req_keys.get('settings', None):
            res = "{}/api/{}/{}/{}/q/{}.{}".format(
                res,
                api,
                req_keys['features'],
                req_keys['settings'],
                req_keys['query'],
                req_keys['format']
                )
        else:
            res = "{}/api/{}/{}/q/{}.{}".format(
                res,
                api,
                req_keys['features'],
                req_keys['query'],
                req_keys['format']
                )
    return res
