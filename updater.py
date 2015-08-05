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
    if verbose:
        print("Getting response from the server...")
    params = kwargs.get('params', None)
    if verbose:
        print("Requesting from {}".format(make_url(**kwargs)))
    # Here is where the script fails if there is no connection
    # wrap the following in a try... except:
    try:
        r = requests.get(make_url(**kwargs), params=params)
    except requests.exceptions.ConnectionError as e:
        # print("bad thing caught in updater.get_response(): {}".format(e))
        # sys.exit()
        tb = sys.exc_info()[2]
        raise e.with_traceback(tb)
    if sys.version_info[1] < 4:
        current_response = r.json
    else:
        current_response = r.json()
    if verbose:
        import pprint
        print('Response keys:')
        pprint.pprint(current_response.keys())
    return current_response


def list_keys(weat_shelve_db):
    import shelve
    print("opening {}...".format(weat_shelve_db))
    fil = shelve.open(weat_shelve_db)
    res = list(fil.keys())
    res.sort()
    print("closing {}...".format(weat_shelve_db))
    fil.close()
    print("sending back list of {} keys...".format(len(res)))
    return res
