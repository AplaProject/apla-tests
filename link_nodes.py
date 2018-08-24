import utils
import config
import requests
import time
import funcs
import os
import json

def isInBlock(call, url, token):
    if "hash" in call:
        status = utils.txstatus(url, 30, call["hash"], token)
        print(status)
        if "blockid" not in status or int(status["blockid"]) < 0:
            print(status)
            return False 
    else:
        return False
    return True
        
def impApp(appName, url, prKey, token):
    path = os.path.join(os.getcwd(), "fixtures", "basic", appName + ".json")
    with open(path, 'r', encoding = "utf8") as f:
        file = f.read()
    files = {'input_file': file}
    resp = utils.call_contract_with_files(url, prKey, "ImportUpload", {},
                                          files, token)
    if("hash" in resp):
        resImportUpload = utils.txstatus(url, 30,
                                         resp["hash"], token)
        if int(resImportUpload["blockid"]) > 0:
            founderID = funcs.call_get_api(url + "/ecosystemparam/founder_account/", "", token)['value']
            result = funcs.call_get_api(url + "/list/buffer_data", "", token)
            buferDataList = result['list']
            for item in buferDataList:
                if item['key'] == "import" and item['member_id'] == founderID:
                    importAppData = json.loads(item['value'])['data']
                    break
            contractName = "Import"
            data = [{"contract": contractName,
                     "params": importAppData[i]} for i in range(len(importAppData))]
            resp = utils.call_multi_contract(url, prKey, contractName, data, token)
            time.sleep(30)
            if "hashes" in resp:
                hashes = resp['hashes']
                result = utils.txstatus_multi(url, 30, hashes, token)
                for status in result.values():
                    print(status)
                    if int(status["blockid"]) < 1:
                        print("Import is failed")
                        exit(1)
                print("App '" + appName + "' successfully installed")
                
def rolesInsatll(url, prKey, token):
    data = {}
    print("RolesInstall started")
    call = utils.call_contract(url, prKey, "RolesInstall",
                               data, token)
    if not isInBlock(call, url, token):
        print("RolesInstall is failed")
        exit(1)
        
def voitingInstall(url, prKey, token):
    data = {}
    print("voitingInstall started")
    call = utils.call_contract(url, prKey, "VotingTemplatesInstall",
                               data, token)
    if not isInBlock(call, url, token):
        print("VoitingInstall is failed")
        exit(1)

    
def editAppParam(name, val, url, prKey, token):
    id = funcs.get_object_id(url, name, "app_params", token)
    print("id", id)
    data = {"Id": id,
            "Name": name, "Value": val, "Conditions": "true" }
    call = utils.call_contract(url, prKey, "EditAppParam",
                               data, token)
    if not isInBlock(call, url, token):
        print("EditAppParam " + name + " is failed")
        exit(1)
    
def updateProfile(name, url, prKey, token):
    time.sleep(5)
    path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
    with open(path, 'rb') as f:
        file = f.read()
    files = {'member_image': file}
    data = {"member_name": name}
    resp = utils.call_contract_with_files(url, prKey, "ProfileEdit",
                                          data, files, token)
    if not isInBlock(resp, url, token):
        print("UpdateProfile " + name + " is failed")
        exit(1)
        
def setAplaConsensus(id, url, prKey, token):
    data = {"member_id": id, "rid": 3}
    call = utils.call_contract(url, prKey, "RolesAssign",
                               data, token)
    if not isInBlock(call, url, token):
        print("RolesAssign " + id + " is failed")
        exit(1)
        
def createVoiting(tcpAdress, apiAddress, keyId, pubKey, url, prKey, token):
    data = {"TcpAddress": tcpAdress, "ApiAddress": apiAddress,
            "KeyId": keyId, "PubKey": pubKey, "Duration": 1}
    print(str(data))
    call = utils.call_contract(url, prKey, "VotingNodeAdd",
                               data, token)
    if not isInBlock(call, url, token):
        print("VotingNodeAdd  is failed")
        exit(1)

def voitingStatusUpdate(url, prKey, token):
    data = {}
    call = utils.call_contract(url, prKey, "VotingStatusUpdate",
                               data, token)
    if not isInBlock(call, url, token):
        print("VoitingStatusUpdate is failed")
        exit(1)
        
def voiting(id, url, prKey, token):
    data = {"votingID": id}
    call = utils.call_contract(url, prKey, "VotingDecisionAccept",
                               data, token)

    if not isInBlock(call, url, token):
        print("VotingDecisionAccept " + id + " is failed")
        exit(1)
        return False
    return True
    

if __name__ == "__main__":
    global dbHost, dbName, login, pas
    conf = config.getNodeConfig()
    url = conf["1"]["url"]
    prKey1 = conf["1"]['private_key']
    prKey2 = conf["2"]['private_key']
    prKey3 = conf["3"]['private_key']
    dbHost = conf["1"]['dbHost']
    dbName = conf["1"]['dbName']
    login = conf["1"]['login']
    pas = conf["1"]['pass']
    data = utils.login(url, prKey1, 0)
    token1 = data["jwtToken"]
    impApp("admin", url, prKey1, token1)
    impApp("system_parameters", url, prKey1, token1)
    impApp("basic", url, prKey1, token1)
    impApp("platform_ecosystem", url, prKey1, token1)
    impApp("language_resources", url, prKey1, token1)
    
    rolesInsatll(url,prKey1, token1)
    
    voitingInstall(url, prKey1, token1)
    editAppParam("voting_sysparams_template_id", 2, url, prKey1, token1)
    node1 = json.dumps({"tcp_address": conf["1"]["tcp_address"],
                      "api_address": conf["1"]["api_address"],
                      "key_id": conf["1"]["keyID"],
                      "public_key": conf["1"]["pubKey"]})
    editAppParam("first_node", node1, url, prKey1, token1)
    
    print("Start create voting 1")
    data = utils.login(url, prKey2, 3)
    token2 = data["jwtToken"]
    createVoiting(conf["2"]["tcp_address"], conf["2"]["api_address"],
                 conf["2"]["keyID"], conf["2"]["pubKey"],
                 url, prKey2, token2)
    voitingStatusUpdate(url, prKey1, token1)
    
    data2 = utils.login(url, prKey2, 0)
    token2 = data2["jwtToken"]
    updateProfile("nodeowner1", url, prKey2, token2)
    data3 = utils.login(url, prKey3, 0)
    token3 = data3["jwtToken"]
    updateProfile("nodeowner2", url, prKey3, token3)
    
    data = utils.login(url, prKey1, 1)
    token1 = data["jwtToken"]
    
    setAplaConsensus(conf["2"]['keyID'], url, prKey1, token1)
    setAplaConsensus(conf["3"]['keyID'], url, prKey1, token1)
    setAplaConsensus(conf["1"]['keyID'], url, prKey1, token1)
    
    data = utils.login(url, prKey3, 3)
    token3 = data["jwtToken"]
    voiting(1, url, prKey3, token3)
    data = utils.login(url, prKey1, 3)
    token1 = data["jwtToken"]
    voiting(1, url, prKey1, token1)
    data = utils.login(url, prKey2, 3)
    token2 = data["jwtToken"]
    voiting(1, url, prKey2, token2)
    
    print("Start create voting 2")
    data = utils.login(url, prKey3, 3)
    token3 = data["jwtToken"]
    createVoiting(conf["3"]["tcp_address"], conf["3"]["api_address"],
                 conf["3"]["keyID"], conf["3"]["pubKey"],
                 url, prKey3, token3)
    voitingStatusUpdate(url, prKey1, token1)
    
    data = utils.login(url, prKey3, 3)
    token3 = data["jwtToken"]
    voiting(2, url, prKey3, token3)
    data = utils.login(url, prKey1, 3)
    token1 = data["jwtToken"]
    voiting(2, url, prKey1, token1)
    data = utils.login(url, prKey2, 3)
    token2 = data["jwtToken"]
    if voiting(2, url, prKey2, token2) == True:
        print("Nodes successfully linked")
        exit(0)