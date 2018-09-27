import requests

from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


def call_get_api(url, data, token):
    resp = requests.get(url, params=data, headers={"Authorization": token})
    if resp.status_code == 200:
        return resp.json()
    else:
        return None


def call_get_api_with_full_response(url, data, token):
    resp = requests.get(url, params=data, headers={"Authorization": token})
    return resp



def call_post_api(url, data, token):
    resp = requests.post(url, data=data, headers={"Authorization": token})
    if resp.status_code == 200:
        return resp.json()
    else:
        return None


def getuid(url):
    endpoint = '/getuid'
    url += endpoint
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        token = result['token']
        uid = result['uid']
        return token, uid
    else:
        return None


def login(url, private_key, role_id=0, ecosystem=1, expire=3600):
    token, uid = getuid(url)
    data_signature = 'LOGIN' + uid
    signature = sign(private_key, data_signature)
    pubkey = get_public_key(private_key)
    full_token = 'Bearer ' + token
    data = {
        'role_id': role_id,
        'ecosystem': ecosystem,
        'expire': expire,
        'pubkey': pubkey,
        'signature': signature,
        # key_id # not use with parameter 'pubkey'
    }
    head = {'Authorization': full_token}
    endpoint = '/login'
    url += endpoint
    response = requests.post(url, data=data, headers=head)
    res = response.json()
    result = {
        'uid': uid,
        'timeToken': res['refresh'],
        'jwtToken': 'Bearer ' + res['token'],
        'pubkey': pubkey,
        'address': res['address'],
        'key_id': res['key_id'],
    }
    return result


def refresh(url, token, expire=36000):
    data = {
        'token': token,
        'expire': expire,
    }
    endpoint = '/refresh'
    url += endpoint
    response = requests.post(url, data=data)
    result = response.json()
    return result


def version(url, token):
    data = {}
    endpoint = '/version'
    url += endpoint
    return call_get_api(url, data, token)


def balance(url, token, key_id):
    data = {}
    endpoint = '/balance/{}'.format(key_id)
    url += endpoint
    return call_get_api(url, data, token)


def ecosystemname(url, token, id=1):
    data = {'id': id}
    endpoint = '/ecosystemname'
    url += endpoint
    return call_get_api(url, data, token)


def appparams(url, token, appid, ecosystem=1, names=''):
    data = {}
    data['ecosystem'] = ecosystem
    if names:
        data['names'] = names
    endpoint = '/appparams/{}'.format(
        appid,
    )
    url += endpoint
    return call_get_api(url, data, token)


def appparam(url, token, appid, name, ecosystem=1):
    data = {'ecosystem': ecosystem}
    endpoint = '/appparam/{}/{}'.format(
        appid,
        name,
    )
    url += endpoint
    return call_get_api(url, data, token)


def ecosystemparams(url, token, ecosystem=1, names=''):
    data = {'ecosystem': ecosystem}
    if names:
        data['names'] = names
    endpoint = '/ecosystemparams'
    url += endpoint
    return call_get_api(url, data, token)


def ecosystemparam(url, token, name, ecosystem=1):
    data = {'ecosystem': ecosystem}
    endpoint = '/ecosystemparam/{}'.format(
        name,
    )
    url += endpoint
    return call_get_api(url, data, token)


def tables(url, token, limit=25, offset=0):
    data = {
        'limit': limit,
        'offset': offset,
    }
    endpoint = '/tables'
    url += endpoint
    print("url", url)
    return call_get_api(url, data, token)


def table(url, token, name):
    data = {}
    endpoint = '/table/{}'.format(
        name,
    )
    url += endpoint
    return call_get_api(url, data, token)


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
    return call_get_api(url, data, token)


def row(url, token, tablename, id, columns=''):
    data = {}
    if columns:
        data['columns'] = columns
    endpoint = '/row/{}/{}'.format(
        tablename,
        id,
    )
    url += endpoint
    return call_get_api(url, data, token)


def systemparams(url, token, names=''):
    data = {}
    if names:
        data['names'] = names
    endpoint = '/systemparams'
    url += endpoint
    return call_get_api(url, data, token)


def history(url, token, name, id):
    data = {}
    endpoint = '/history/{}/{}'.format(
        name,
        id,
    )
    url += endpoint
    return call_get_api(url, data, token)


def interface(url, token, entity, name):
    """ Parameter entity must be 'page', 'menu' or 'block' """
    data = {}
    endpoint = '/interface/{}/{}'.format(
        entity,
        name,
    )
    url += endpoint
    return call_get_api(url, data, token)


def contracts(url, token, limit=25, offset=0):
    data = {
        'limit': limit,
        'offset': offset,
    }
    endpoint = '/contracts'
    url += endpoint
    return call_get_api(url, data, token)


def contract(url, token, name):
    data = {}
    endpoint = '/contract/{}'.format(
        name,
    )
    url += endpoint
    return call_get_api(url, data, token)


# contract/{request_id}
# contractMultiple/{request_id}
# prepare/{name}
# prepareMultiple
# txstatus/{hash}
# txstatusMultiple


def content(url, token, entity, name, lang='en-US', app_id=1):
    """ Parameter entity must be 'page' or 'menu' """
    data = {
        'lang': lang,
        'app_id': app_id,
    }
    endpoint = '/content/{}/{}'.format(
        entity,
        name,
    )
    url += endpoint
    return call_post_api(url, data, token)


def content_source(url, token, name):
    data = {}
    endpoint = 'content/source/{}'.format(
        name,
    )
    url += endpoint
    return call_post_api(url, data, token)


def content_hash(url, token, name):
    data = {}
    endpoint = 'content/hash/{}'.format(
        name,
    )
    url += endpoint
    return call_post_api(url, data, token)


def content_template(url, token, template, source=0):
    data = {
        'template': template,
        'source': source,
    }
    endpoint = '/content'
    url += endpoint
    return call_post_api(url, data, token)


# node/{name} - only VDE


def maxblockid(url, token):
    data = {}
    endpoint = '/maxblockid'
    url += endpoint
    return call_get_api(url, data, token)


def block(url, token, id):
    data = {}
    endpoint = '/block/{}'.format(
        id,
    )
    url += endpoint
    return call_get_api(url, data, token)


def avatar(url, token, member, ecosystem=1):
    data = {}
    endpoint = '/avatar/{}/{}'.format(
        ecosystem,
        member,
    )
    url += endpoint
    return call_get_api_with_full_response(url, data, token)


def config_centrifugo(url, token):
    data = {}
    endpoint = '/config/centrifugo'
    url += endpoint
    return call_get_api(url, data, token)


if __name__ == 'main':
    pass
