import random
import string
import requests
import psycopg2
import json
import time

from collections import Counter
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


class Actions(object):

    def get_uid(url):
        resp = requests.get(url + '/getuid')
        result = resp.json()
        return result['token'], result['uid']

    def login(url, prKey, role=0, ecosystem=1):
        token, uid = Actions.get_uid(url)
        signature = sign(prKey, "LOGIN" + uid)
        pubkey = get_public_key(prKey)
        fullToken = 'Bearer ' + token
        data = {'pubkey': pubkey, 'signature': signature, "role_id": role, "ecosystem": ecosystem}
        head = {'Authorization': fullToken}
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

    def prepare_tx(url, prKey, entity, jvtToken, data):
        heads = {'Authorization': jvtToken}
        resp = requests.post(url + '/prepare/' + entity, data=data, headers=heads)
        result = resp.json()
        signature = sign(prKey, result['forsign'])
        return {"time": result['time'], "signature": signature, "reqID": result['request_id']}

    def prepare_tx_with_files(url, prKey, entity, jvtToken, data, files):
        heads = {'Authorization': jvtToken}
        resp = requests.post(url + '/prepare/' + entity,
                             data=data, headers=heads, files=files)
        result = resp.json()
        signature = sign(prKey, result['forsign'])
        return {"time": result['time'], "signature": signature, "reqID": result['request_id']}

    def call_contract(url, prKey, name, data, jvtToken):
        sign = Actions.prepare_tx(url, prKey, name, jvtToken, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        urlEnd = url + '/contract/' + sign["reqID"]
        resp = requests.post(urlEnd, data=dataContract, headers={"Authorization": jvtToken})
        result = resp.json()
        return result

    def prepare_multi_tx(url, prKey, entity, jvtToken, data):
        urlToCont = url + '/prepareMultiple/'
        heads = {'Authorization': jvtToken}
        request = {"token_ecosystem": "",
                   "max_sum": "",
                   "payover": "",
                   "signed_by": "",
                   "contracts": data}
        resp = requests.post(urlToCont, data={"data": json.dumps(request)}, headers=heads)
        result = resp.json()
        forsigns = result['forsign']
        signatures = [sign(prKey, forsign) for forsign in forsigns]
        return {"time": result['time'], "signatures": signatures, "reqID": result['request_id']}

    def call_multi_contract(url, prKey, name, data, jvtToken):
        sign = Actions.prepare_multi_tx(url, prKey, name, jvtToken, data)
        dataContract = {"time": sign['time'], "signatures": sign["signatures"]}
        urlEnd = url + '/contractMultiple/' + sign["reqID"]
        resp = requests.post(urlEnd, data={"data": json.dumps(dataContract)}, headers={"Authorization": jvtToken})
        result = resp.json()
        return result

    def call_contract_with_files(url, prKey, name, data, files, jvtToken):
        sign = Actions.prepare_tx_with_files(url, prKey, name, jvtToken, data, files)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        urlEnd = url + '/contract/' + sign["reqID"]
        resp = requests.post(urlEnd, data=dataContract,
                             headers={"Authorization": jvtToken})
        result = resp.json()
        return result

    def tx_status(url, sleepTime, hsh, jvtToken):
        sec = 0
        urlEnd = url + '/txstatus/' + hsh
        while sec < sleepTime:
            time.sleep(1)
            resp = requests.get(urlEnd, headers={'Authorization': jvtToken})
            jresp = resp.json()
            if (len(jresp['blockid']) > 0 and 'errmsg' not in json.dumps(jresp)) or ('errmsg' in json.dumps(jresp)):
                status = resp.json()
            else:
                sec = sec + 1        
        if 'errmsg' not in status and int(status['blockid']) > 0:
            return {"blockid": int(status['blockid']), "result": status['result'],
                "error": None}
        else:
            return {"blockid": 0, "error": status['errmsg']['error'], "result": None}


    def tx_status_multi(url, sleepTime, hshs, jvtToken):
        urlEnd = url + '/txstatusMultiple/'
        allTxInBlocks = False
        sec = 0
        while sec < sleepTime:
            time.sleep(1)
            resp = requests.post(urlEnd, params={"data": json.dumps({"hashes": hshs})},
                                 headers={'Authorization': jvtToken})
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
        resp = requests.get(url, data=data,  headers={"Authorization": token})
        return resp.json()

    def call_get_api_with_full_response(url, data, token):
        resp = requests.get(url, data=data,  headers={"Authorization": token})
        return resp

    def call_post_api(url, data, token):
        resp = requests.post(url, data=data,  headers={"Authorization": token})
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def get_count(self, url, type, token):
        endPoint = url + "/list/" + type
        res = self.call_get_api(endPoint, "", token)
        return res["count"]

    def get_list(self, url, type, token):
        count = self.get_count(url, type, token)
        endPoint = url + "/list/" + type + "?limit=" + count
        res = self.call_get_api(endPoint, "", token)
        return res

    def get_contract_id(self, url, name, token):
        endPoint = url + "/contract/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["tableid"]


    def get_object_id(self, url, name, object, token):
        id = None
        endPoint = url + "/list/" + object
        res = self.call_get_api(endPoint, "", token)
        for object in res["list"]:
            if object["name"] == name:
                id = object["id"]
        return id
    

    def is_contract_activated(self, url, name, token):
        endPoint = url + "/contract/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["active"]

    def get_activated_wallet(self, url, name, token):
        endPoint = url + "/contract/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["walletid"]

    def get_parameter_id(self, url, name, token):
        endPoint = url + "/ecosystemparam/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["id"]

    def get_parameter_value(self, url, name, token):
        endPoint = url + "/ecosystemparam/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["value"]

    def get_content(self, url, type, name, lang, appId, token):
        if(lang != ""):
            data = {"lang": lang, "app_id": appId}
        else:
            data = ""
        endPoint = url + "/content/" + type + "/" + name
        res = self.call_post_api(endPoint, data, token)
        return res

    def get_max_block_id(self, url, token):
        data = ""
        endPoint = url + "/maxblockid"
        result = self.call_get_api(endPoint, data, token)
        return result["max_block_id"]
