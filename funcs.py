import requests
import json


def call_get_api(url, data, token):
    resp = requests.get(url, data=data,  headers={"Authorization": token})
    return resp.json()

def call_post_api(url, data, token):
    resp = requests.post(url, data=data,  headers={"Authorization": token})
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

def get_count(url, type, token):
    endPoint = url + "/list/" + type
    res = call_get_api(endPoint, "", token)
    return res["count"]

def get_contract_id(url, name, token):
    endPoint = url + "/contract/" + name
    res = call_get_api(endPoint, "", token)
    return res["tableid"]

def get_parameter_id(url, name, token):
    endPoint = url + "/ecosystemparam/" + name
    res = call_get_api(endPoint, "", token)
    return res["id"]

def get_parameter_value(url, name, token):
    endPoint = url + "/ecosystemparam/" + name
    res = call_get_api(endPoint, "", token)
    return res["value"]

def get_content(url, type, name, lang, token):
    if(lang != ""):
        data = {"lang": lang}
    else:
        data = ""
    endPoint = url + "/content/" + type + "/" + name
    res = call_post_api(endPoint, data, token)
    return res

def get_max_block_id(url, token):
    data = ""
    endPoint = url + "/maxblockid"
    result = call_get_api(endPoint, data, token)
    if (result != None):
        return result["max_block_id"]
    else:
        return None