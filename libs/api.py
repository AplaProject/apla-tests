import random
import string
import requests
import psycopg2
import json
import time
from libs import actions

from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


#getuid
#login
#refresh


def version(url, token):
    data = {}
    endpoint = '/version'
    url += endpoint
    return actions.call_get_api(url, data, token)


def balance(url, token, key_id):
    data = {}
    endpoint = '/balance/{}'.format(key_id)
    url += endpoint
    return actions.call_get_api(url, data, token)


def ecosystemname(url, token, id=1):
    data = {'id': id}
    endpoint = '/ecosystemname'
    url += endpoint
    print(url)
    return actions.call_get_api(url, data, token)


def appparams(url, token, appid, ecosystem=1, names=''):
    data = {}
    data['ecosystem'] = ecosystem
    if names:
        data['names'] = names
    endpoint = '/appparams/{}'.format(
        appid,
    )
    url += endpoint
    print(data)
    return actions.call_get_api(url, data, token)


def appparam(url, token, appid, name, ecosystem=1):
    data = {'ecosystem': ecosystem}
    endpoint = '/appparam/{}/{}'.format(
        appid,
        name,
    )
    url += endpoint
    return actions.call_get_api(url, data, token)


def ecosystemparams(url, token, ecosystem=1, names=''):
    data = {'ecosystem': ecosystem}
    if names:
        data['names'] = names
    endpoint = '/ecosystemparams'
    url += endpoint
    return actions.call_get_api(url, data, token)


def ecosystemparam(url, token, name, ecosystem=1):
    data = {'ecosystem': ecosystem}
    endpoint = '/ecosystemparam/{}'.format(
        name,
    )
    url += endpoint
    return actions.call_get_api(url, data, token)


def tables(url, token, limit=25, offset=0):
    data = {
        'limit': limit,
        'offset': offset,
    }
    endpoint = '/tables'
    url += endpoint
    return actions.call_get_api(url, data, token)


def table(url, token, name):
    data = {}
    endpoint = '/table/{}'.format(
        name,
    )
    url += endpoint
    return actions.call_get_api(url, data, token)


def list(url, token, name, limit=25, offset=0, columns=''):
    data = {
        'limit': limit,
        'offset': offset,
    }
    if columns:
        data['columns'] = columns
    endpoint = '/list/{}'.format(
        name,
    )
    url += endpoint
    return actions.call_get_api(url, data, token)


def row(url, token, tablename, id, columns=''):
    data = {}
    if columns:
        data['columns'] = columns
    endpoint = '/row/{}/{}'.format(
        tablename,
        id,
    )
    url += endpoint
    return actions.call_get_api(url, data, token)


def systemparams(url, token, names=''):
    data = {}
    if names:
        data['names'] = names
    endpoint = '/systemparams'
    url += endpoint
    return actions.call_get_api(url, data, token)


def history(url, token, name, id):
    data = {}
    endpoint = '/history/{}/{}'.format(
        name,
        id,
    )
    url += endpoint
    return actions.call_get_api(url, data, token)