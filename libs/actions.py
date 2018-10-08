import requests
import json
import time

from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key
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
    result["timeToken"] = res["refresh"]
    result["jwtToken"] = 'Bearer ' + res["token"]
    result["pubkey"] = pubkey
    result["address"] = res["address"]
    result["key_id"] = res["key_id"]
    return result

def prepare_tx(url, pr_key, entity, jvt_token, data):
    heads = {'Authorization': jvt_token}
    resp = requests.post(url + '/prepare/' + entity, data=data, headers=heads)
    result = resp.json()
    signature = sign(pr_key, result['forsign'])
    return {"time": result['time'], "signature": signature, "reqID": result['request_id']}

def prepare_tx_with_files(url, pr_key, entity, jvt_token, data, files):
    heads = {'Authorization': jvt_token}
    resp = requests.post(url + '/prepare/' + entity,
                        data=data, headers=heads, files=files)
    result = resp.json()
    signature = sign(pr_key, result['forsign'])
    return {"time": result['time'], "signature": signature, "reqID": result['request_id']}

def call_contract(url, pr_key, name, data, jvt_token):
    sign = prepare_tx(url, pr_key, name, jvt_token, data)
    data_contract = {"time": sign['time'], "signature": sign["signature"]}
    url_end = url + '/contract/' + sign["reqID"]
    resp = requests.post(url_end, data=data_contract, headers={"Authorization": jvt_token})
    result = resp.json()
    return result

def prepare_multi_tx(url, pr_key, entity, jvt_token, data):
    url_to_cont = url + '/prepareMultiple/'
    heads = {'Authorization': jvt_token}
    request = {"token_ecosystem": "", "max_sum": "","payover": "",
               "signed_by": "", "contracts": data}
    resp = requests.post(url_to_cont, data={"data": json.dumps(request)}, headers=heads)
    result = resp.json()
    forsigns = result['forsign']
    signatures = [sign(pr_key, forsign) for forsign in forsigns]
    return {"time": result['time'], "signatures": signatures, "reqID": result['request_id']}

def call_multi_contract(url, pr_key, name, data, jvt_token):
    sign = prepare_multi_tx(url, pr_key, name, jvt_token, data)
    data_contract = {"time": sign['time'], "signatures": sign["signatures"]}
    url_end = url + '/contractMultiple/' + sign["reqID"]
    resp = requests.post(url_end, data={"data": json.dumps(data_contract)},
                         headers={"Authorization": jvt_token})
    result = resp.json()
    return result

def call_contract_with_files(url, pr_key, name, data, files, jvt_token):
    sign = prepare_tx_with_files(url, pr_key, name, jvt_token, data, files)
    data_contract = {"time": sign['time'], "signature": sign["signature"]}
    url_end = url + '/contract/' + sign["reqID"]
    resp = requests.post(url_end, data=data_contract, headers={"Authorization": jvt_token})
    result = resp.json()
    return result

def tx_status(url, sleep_time, hsh, jvt_token):
    sec = 0
    url_end = url + '/txstatus/' + hsh
    while sec < sleep_time:
        time.sleep(1)
        resp = requests.get(url_end, headers={'Authorization': jvt_token})
        jresp = resp.json()
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
    url_end = url + '/txstatusMultiple/'
    all_tx_in_blocks = False
    sec = 0
    while sec < sleep_time:
        time.sleep(1)
        resp = requests.post(url_end, params={"data": json.dumps({"hashes": hshs})},
                             headers={'Authorization': jvt_token})
        jresp = resp.json()["results"]
        for status in jresp.values():
            if (len(status['blockid']) > 0 and 'errmsg' not in json.dumps(status)):
                all_tx_in_blocks = True
            else:
                all_tx_in_blocks = False
        if all_tx_in_blocks == True:
            return jresp
        else:
            sec = sec + 1
    return jresp

        
def call_get_api(url, data, token):
    resp = requests.get(url, params=data,  headers={"Authorization": token})
    print("resp", resp)
    print(resp.json())
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

def call_get_api_with_full_response(url, data, token):
    resp = requests.get(url, params=data,  headers={"Authorization": token})
    return resp

def call_post_api(url, data, token):
    resp = requests.post(url, data=data,  headers={"Authorization": token})
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

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
    print("res", res)
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
