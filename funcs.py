import requests
import json


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

def find_id_by_name(url, token, table, name):
    # get_list must have column 'name', else Error
    answer_dict = get_list(url, table, token)['list']
    print(answer_dict)
    for element in range(len(answer_dict)):
        if answer_dict[element]['name'] == name:
            return answer_dict[element]['id']
        else:
            return None

def get_count(url, type, token):
    endPoint = url + "/list/" + type
    res = call_get_api(endPoint, "", token)
    return res["count"]

def get_list(url, type, token):
    count = get_count(url, type, token)
    endPoint = url + "/list/" + type + "?limit=" + count
    res = call_get_api(endPoint, "", token)
    return res

def get_contract_id(url, name, token):
    endPoint = url + "/contract/" + name
    res = call_get_api(endPoint, "", token)
    return res["tableid"]

def get_application_id(url, name, token):
    id = None
    endPoint = url + "/list/applications"
    res = call_get_api(endPoint, "", token)
    for app in res["list"]:
        if app["name"] == name:
            id = app["id"]
    return id

def get_object_id(url, name, object, token):
    id = None
    endPoint = url + "/list/" + object + "?limit=1000"
    print("endPoint", endPoint)
    res = call_get_api(endPoint, "", token)
    print("ans", res)
    print("name", name)
    for object in res["list"]:
        if object["name"] == name:
            id = object["id"]
    return id
    

def is_contract_activated(url, name, token):
    endPoint = url + "/contract/" + name
    res = call_get_api(endPoint, "", token)
    print(res)
    return res["active"]

def get_activated_wallet(url, name, token):
    endPoint = url + "/contract/" + name
    res = call_get_api(endPoint, "", token)
    return res["walletid"]

def get_parameter_id(url, name, token):
    endPoint = url + "/ecosystemparam/" + name
    res = call_get_api(endPoint, "", token)
    return res["id"]

def get_parameter_value(url, name, token):
    endPoint = url + "/ecosystemparam/" + name
    res = call_get_api(endPoint, "", token)
    return res["value"]

def get_content(url, type, name, lang, appId, token):
    if(lang != ""):
        data = {"lang": lang, "app_id": appId}
    else:
        data = ""
    endPoint = url + "/content/" + type + "/" + name
    res = call_post_api(endPoint, data, token)
    return res

def get_max_block_id(url, token):
    data = ""
    endPoint = url + "/maxblockid"
    result = call_get_api(endPoint, data, token)
    return result["max_block_id"]