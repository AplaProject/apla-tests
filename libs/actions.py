import requests
import json
import time

from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key
from genesis_blockchain_tools.contract import Contract
from libs import api

def get_uid(url):
    resp = requests.get(url + '/getuid')
    result = resp.json()
    return result['token'], result['uid']

def login(url, pr_key, role=0, ecosystem=1):
    token, uid = get_uid(url)
    signature = sign(pr_key, "LOGIN" + uid)
    pubkey = get_public_key(pr_key)
    full_token = 'Bearer ' + token
    data = {'pubkey': pubkey, 'signature': signature, "role_id": role, "ecosystem": ecosystem}
    head = {'Authorization': full_token}
    resp = requests.post(url + '/login', params=data, headers=head)
    res = resp.json()
    result = {}
    result["uid"] = uid
    result["jwtToken"] = 'Bearer ' + res["token"]
    result["pubkey"] = pubkey
    result["address"] = res["address"]
    result["key_id"] = res["key_id"]
    return result


def get_schema(url, name, jvtToken):
    resp = requests.get(url + '/contract/' + name, headers={"Authorization": jvtToken})
    return resp.json()


def call_contract(url, prKey, name, data, jvtToken, ecosystem=1):
    schema = get_schema(url, name, jvtToken)
    contract = Contract(schema=schema,
                        private_key=prKey,
                        ecosystem_id=ecosystem,
                        params=data)
    tx_bin_data = contract.concat()
    resp = requests.post(url + '/sendTx', files={'call1': tx_bin_data},
                        headers={"Authorization": jvtToken})
    result = resp.json()
    if 'hashes' in result:
        return result['hashes']['call1']
    else:
        return result


def call_multi_contract(url, prKey, name, data, jvtToken, withData=True):
    full_bindata = {}
    i = 1
    for inf in data:
        if withData == True and inf['params']['Data'] == '[]':
            continue
        schema = get_schema(url, inf['contract'], jvtToken)
        contract = Contract(schema=schema, private_key=prKey,
                    params=inf['params'])
        tx_bin_data = contract.concat()
        full_bindata.update({'call' + str(i): tx_bin_data})
        i += 1
    resp = requests.post(url + '/sendTx', files=full_bindata,
                        headers={"Authorization": jvtToken})
    result = resp.json()
    return result


def tx_status(url, sleep_time, hsh, jvt_token):
    sec = 0
    url_end = url + '/txstatus'
    while sec < sleep_time:
        time.sleep(1)
        resp = requests.post(url_end, params={"data": json.dumps({"hashes": [hsh]})},
                             headers={'Authorization': jvt_token})
        jresp = resp.json()["results"][hsh]
        status = {}
        if (len(jresp['blockid']) > 0 and 'errmsg' not in json.dumps(jresp)) or ('errmsg' in json.dumps(jresp)):
            break
        else:
            sec = sec + 1  
    if 'errmsg' not in jresp and jresp['blockid'] == '':
        return {"blockid": None, "result": None, "error": None}     
    if 'errmsg' not in jresp and int(jresp['blockid']) > 0:
        return {"blockid": int(jresp['blockid']), "result": jresp['result'], "error": None}
    else:
        return {"blockid": 0, "error": jresp['errmsg']['error'], "result": None}


def tx_status_multi(url, sleep_time, hshs, jvt_token):
    url_end = url + '/txstatus'
    allTxInBlocks = False
    sec = 0
    list = []
    for hash in hshs:
        list.append(hshs[hash])
    while sec < sleep_time:
        time.sleep(1)
        resp = requests.post(url_end, params={"data": json.dumps({"hashes": list})},
                             headers={'Authorization': jvt_token})
        jresp = resp.json()["results"]
        for status in jresp.values():
            if (len(status['blockid']) > 0 and 'errmsg' not in json.dumps(status)):
                allTxInBlocks = True
            else:
                allTxInBlocks = False
        if allTxInBlocks == True:
            return jresp
        else:
            sec = sec + 1
    return jresp

        
def call_get_api(url, data, token):
    resp = requests.get(url, params=data,  headers={"Authorization": token})
    return resp.json()

def call_get_api_with_full_response(url, data, token):
    resp = requests.get(url, params=data,  headers={"Authorization": token})
    return resp

def call_post_api(url, data, token):
    resp = requests.post(url, data=data,  headers={"Authorization": token})
    return resp.json()

def get_count(url, type, token):
    end_point = url + "/list/" + type
    res = call_get_api(end_point, "", token)
    return res["count"]

def get_list(url, type, token):
    count = get_count(url, type, token)
    end_point = url + "/list/" + type + "?limit=" + count
    res = call_get_api(end_point, "", token)
    return res

def get_contract_id(url, name, token):
    end_point = url + "/contract/" + name
    res = call_get_api(end_point, "", token)
    return res["tableid"]


def get_object_id(url, name, object, token):
    id = None
    end_point = url + "/list/" + object + "?limit=1000"
    res = call_get_api(end_point, "", token)
    for object in res["list"]:
        if object["name"] == name:
            id = object["id"]
    return id
    

def is_contract_activated(url, name, token):
    end_point = url + "/contract/" + name
    res = call_get_api(end_point, "", token)
    return res["active"]

def get_activated_wallet(url, name, token):
    end_point = url + "/contract/" + name
    res = call_get_api(end_point, "", token)
    return res["walletid"]

def get_parameter_id(url, name, token):
    end_point = url + "/ecosystemparam/" + name
    res = call_get_api(end_point, "", token)
    return res["id"]

def get_parameter_value(url, name, token):
    end_point = url + "/ecosystemparam/" + name
    res = call_get_api(end_point, "", token)
    return res["value"]

def get_sysparam_value(url, token, name):
    list = api.systemparams(url, token, name)
    return list['list'][0]['value']

def get_content(url, type, name, lang, appId, token):
    if(lang != ""):
        data = {"lang": lang, "app_id": appId}
    else:
        data = ""
    end_point = url + "/content/" + type + "/" + name
    res = call_post_api(end_point, data, token)
    return res

def get_max_block_id(url, token):
    data = ""
    end_point = url + "/maxblockid"
    result = call_get_api(end_point, data, token)
    return result["max_block_id"]
