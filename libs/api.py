import requests
import json

from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


def call_get_api(url, data, token):
    resp = requests.get(
        url,
        params=data,
        headers={'Authorization': token}
    )
    return resp.json()


def call_get_api_with_full_response(url, data, token):
    resp = requests.get(
        url,
        params=data,
        headers={'Authorization': token}
    )
    return resp


def call_post_api(url, data, token):
    resp = requests.post(
        url,
        data=data,
        headers={'Authorization': token}
    )
    return resp.json()


def getuid(url):
    endpoint = '/getuid'
    url += endpoint
    response = requests.get(url)
    result = response.json()
    token = result['token']
    uid = result['uid']
    return token, uid


def login(url, token, uid, private_key, role_id=0, ecosystem=1, expire=3600):
    signature = sign(private_key, 'LOGIN' + uid)
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
    endpoint = '/login'
    url += endpoint
    res = call_post_api(url, data, full_token)
    print(res)
    result = {
        'uid': uid,
        'jwtToken': 'Bearer ' + res['token'],
        'pubkey': pubkey,
        'address': res['address'],
        'key_id': res['key_id'],
        'ecosystem_id': res['ecosystem_id']
    }
    return result


def version(url, token):
    data = {}
    endpoint = '/version'
    url += endpoint
    return call_get_api(url, data, token)


def balance(url, token, key_id):
    data = {}
    endpoint = '/balance/{key_id}'.format(
        key_id=key_id
    )
    url += endpoint
    return call_get_api(url, data, token)


def keyinfo(url, token, key_id):
    data = {}
    endpoint = '/keyinfo/{key_id}'.format(
        key_id=key_id
    )
    url += endpoint
    return call_get_api(url, data, token)


def ecosystemname(url, token, id=1):
    data = {'id': id}
    endpoint = '/ecosystemname'
    url += endpoint
    return call_get_api(url, data, token)


def ecosystems(url, token):
    data = {}
    endpoint = '/ecosystems'
    url += endpoint
    return call_get_api(url, data, token)


def appparams(url, token, appid, ecosystem=1, names=''):
    data = {}
    data['ecosystem'] = ecosystem
    if names:
        data['names'] = names
    endpoint = '/appparams/{appid}'.format(
        appid=appid
    )
    url += endpoint
    return call_get_api(url, data, token)


def appparam(url, token, appid, name, ecosystem=1):
    data = {'ecosystem': ecosystem}
    endpoint = '/appparam/{appid}/{name}'.format(
        appid=appid,
        name=name
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
    endpoint = '/ecosystemparam/{name}'.format(
        name=name
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
    return call_get_api(url, data, token)


def table(url, token, name):
    data = {}
    endpoint = '/table/{name}'.format(
        name=name
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
    endpoint = '/list/' + name
    url += endpoint
    return call_get_api(url, data, token)


def sections(url, token, limit=25, offset=0, lang='en-US'):
    data = {
        'limit': limit,
        'offset': offset,
        'lang': lang,
    }
    endpoint = '/sections'
    url += endpoint
    return call_get_api(url, data, token)


def row(url, token, tablename, id, columns=''):
    data = {}
    if columns:
        data['columns'] = columns
    endpoint = '/row/{tablename}/{id}'.format(
        tablename=tablename,
        id=id
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
    endpoint = '/history/{name}/{id}'.format(
        name=name,
        id=id
    )
    url += endpoint
    return call_get_api(url, data, token)


def interface(url, token, entity, name):
    """ Parameter entity must be 'page', 'menu' or 'block' """
    data = {}
    endpoint = '/interface/{entity}/{name}'.format(
        entity=entity,
        name=name
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
    endpoint = '/contract/{name}'.format(
        name=name
    )
    url += endpoint
    return call_get_api(url, data, token)


def send_tx(url, token, tx_bin_data):
    endpoint = '/sendTx'
    url += endpoint
    resp = requests.post(
        url,
        files=tx_bin_data,
        headers={'Authorization': token}
    )
    result = resp.json()
    return result


def tx_status(url, token, hashes):
    hashes_data = json.dumps({'hashes': [hashes]})
    data = {'data': hashes_data}
    endpoint = '/txstatus'
    url += endpoint
    res = call_post_api(url, data, token)
    return res


def tx_info(url, token, hash, contract_info=False):
    data = {'contractinfo': contract_info}
    endpoint = '/txinfo/{hash}'.format(
        hash=hash
    )
    url += endpoint
    return call_get_api(url, data, token)


def tx_info_multiple(url, token, hashes, contract_info=False):
    data = {
        'data': hashes,
        'contractinfo': contract_info,
    }
    endpoint = '/txinfoMultiple'
    url += endpoint
    return call_get_api(url, data, token)


def content(url, token, entity, name, lang='en-US', app_id=1, page_params={}):
    """ Parameter entity must be 'page' or 'menu' """
    data = {
        'lang': lang,
        'app_id': app_id,
    }
    for key, value in page_params.items():
        data.update({key: value})
    endpoint = '/content/{entity}/{name}'.format(
        entity=entity,
        name=name
    )
    url += endpoint
    return call_post_api(url, data, token)


def content_source(url, token, name):
    data = {}
    endpoint = '/content/source/{name}'.format(
        name=name
    )
    url += endpoint
    return call_post_api(url, data, token)


def content_hash(url, token, name):
    data = {}
    endpoint = '/content/hash/{name}'.format(
        name=name
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
    endpoint = '/block/{id}'.format(
        id=id
    )
    url += endpoint
    return call_get_api(url, data, token)


def avatar(url, token, member, ecosystem=1):
    data = {}
    endpoint = '/avatar/{ecosystem}/{member}'.format(
        ecosystem=ecosystem,
        member=member
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
