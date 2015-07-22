#! /usr/local/bin/python3
# coding=utf-8

# -----------------------------------------------------------------------------
#         file:     updater.py
#       author:     dpomondo
# dependencies:     imported and called from getter.py, returner.py
#
# -----------------------------------------------------------------------------
import requests
import sys


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


def get_response(verbose=False, **kwargs):
    """ Fill the current_response object with the json returned
    from the website
    """
    import pprint
    if verbose:
        print("Getting response from the server...")
    params = kwargs.get('params', None)
    if verbose:
        print("Requesting from {}".format(make_url(**kwargs)))
    r = requests.get(make_url(**kwargs), params=params)
    if sys.version_info[1] < 4:
        current_response = r.json
    else:
        current_response = r.json()
    if verbose:
        print('Response keys:')
        pprint.pprint(current_response.keys())
    return current_response
