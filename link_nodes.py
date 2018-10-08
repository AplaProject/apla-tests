import time
import os
import json

from libs import actions, tools

def is_in_block(call, url, token):
    if "hash" in call:
        status = actions.tx_status(url, 30, call["hash"], token)
        print(status)
        if "blockid" not in status or int(status["blockid"]) < 0:
            print(status)
            return False 
    else:
        return False
    return True
        
def imp_app(app_name, url, pr_key, token):
    path = os.path.join(os.getcwd(), "fixtures", "basic", app_name + ".json")
    with open(path, 'r', encoding = "utf8") as f:
        file = f.read()
    files = {'input_file': file}
    resp = actions.call_contract_with_files(url, pr_key, "ImportUpload", {},
                                            files, token)
    if("hash" in resp):
        res_import_upload = actions.tx_status(url, 30,
                                         resp["hash"], token)
        if int(res_import_upload["blockid"]) > 0:
            founder_id = actions.call_get_api(url + "/ecosystemparam/founder_account/", "", token)['value']
            result = actions.call_get_api(url + "/list/buffer_data", "", token)
            bufer_data_list = result['list']
            for item in bufer_data_list:
                if item['key'] == "import" and item['member_id'] == founder_id:
                    import_app_data = json.loads(item['value'])['data']
                    break
            contract_name = "Import"
            data = [{"contract": contract_name,
                     "params": import_app_data[i]} for i in range(len(import_app_data))]
            resp = actions.call_multi_contract(url, pr_key, contract_name, data, token)
            time.sleep(30)
            if "hashes" in resp:
                hashes = resp['hashes']
                result = actions.tx_status_multi(url, 30, hashes, token)
                for status in result.values():
                    print(status)
                    if int(status["blockid"]) < 1:
                        print("Import is failed")
                        exit(1)
                print("App '" + app_name + "' successfully installed")
                
def roles_install(url, pr_key, token):
    data = {}
    print("RolesInstall started")
    call = actions.call_contract(url, pr_key, "RolesInstall",
                                 data, token)
    if not is_in_block(call, url, token):
        print("RolesInstall is failed")
        exit(1)
        
def voiting_install(url, pr_key, token):
    data = {}
    print("voiting_install started")
    call = actions.call_contract(url, pr_key, "VotingTemplatesInstall",
                               data, token)
    if not is_in_block(call, url, token):
        print("VoitingInstall is failed")
        exit(1)

    
def edit_app_param(name, val, url, pr_key, token):
    id = actions.get_object_id(url, name, "app_params", token)
    print("id", id)
    data = {"Id": id,
            "Name": name, "Value": val, "Conditions": "true" }
    call = actions.call_contract(url, pr_key, "EditAppParam",
                               data, token)
    if not is_in_block(call, url, token):
        print("EditAppParam " + name + " is failed")
        exit(1)
    
def update_profile(name, url, pr_key, token):
    time.sleep(5)
    path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
    with open(path, 'rb') as f:
        file = f.read()
    files = {'member_image': file}
    data = {"member_name": name}
    resp = actions.call_contract_with_files(url, pr_key, "ProfileEdit",
                                          data, files, token)
    if not is_in_block(resp, url, token):
        print("UpdateProfile " + name + " is failed")
        exit(1)
        
def set_apla_consensus(id, url, pr_key, token):
    data = {"member_id": id, "rid": 3}
    call = actions.call_contract(url, pr_key, "RolesAssign",
                               data, token)
    print("--------------------------------------------------------------------------")
    print("setAplaconsensus block: ", call)
    if not is_in_block(call, url, token):
        print("RolesAssign " + id + " is failed")
        exit(1)
        
def create_voiting(tcp_address, api_address, key_id, pub_key, url, pr_key, token):
    data = {"TcpAddress": tcp_address, "ApiAddress": api_address,
            "KeyId": key_id, "PubKey": pub_key, "Duration": 1}
    print(str(data))
    call = actions.call_contract(url, pr_key, "VotingNodeAdd",
                               data, token)
    if not is_in_block(call, url, token):
        print("VotingNodeAdd  is failed")
        exit(1)

def voting_status_update(url, pr_key, token):
    data = {}
    call = actions.call_contract(url, pr_key, "VotingStatusUpdate",
                               data, token)
    if not is_in_block(call, url, token):
        print("VoitingStatusUpdate is failed")
        exit(1)
        
def voiting(id, url, pr_key, token):
    data = {"votingID": id}
    call = actions.call_contract(url, pr_key, "VotingDecisionAccept",
                               data, token)

    if not is_in_block(call, url, token):
        print("VotingDecisionAccept " + id + " is failed")
        exit(1)
        return False
    return True
    

if __name__ == "__main__":
    conf = tools.read_config("nodes")
    url = conf[0]["url"]
    pr_key1 = conf[0]['private_key']
    pr_key2 = conf[1]['private_key']
    pr_key3 = conf[2]['private_key']
    data = actions.login(url, pr_key1, 0)
    token1 = data["jwtToken"]
    imp_app("admin", url, pr_key1, token1)
    imp_app("system_parameters", url, pr_key1, token1)
    imp_app("basic", url, pr_key1, token1)
    imp_app("platform_ecosystem", url, pr_key1, token1)
    imp_app("language_resources", url, pr_key1, token1)
    
    roles_install(url, pr_key1, token1)
    
    voiting_install(url, pr_key1, token1)
    edit_app_param("voting_sysparams_template_id", 2, url, pr_key1, token1)
    node1 = json.dumps({"tcp_address": conf[0]["tcp_address"],
                      "api_address": conf[0]["api_address"],
                      "key_id": conf[0]["keyID"],
                      "public_key": conf[0]["pubKey"]})
    edit_app_param("first_node", node1, url, pr_key1, token1)
    
    data2 = actions.login(url, pr_key2, 0)
    token2 = data2["jwtToken"]
    update_profile("nodeowner1", url, pr_key2, token2)
    data3 = actions.login(url, pr_key3, 0)
    token3 = data3["jwtToken"]
    update_profile("nodeowner2", url, pr_key3, token3)
    
    data = actions.login(url, pr_key1, 1)
    token1 = data["jwtToken"]
    
    set_apla_consensus(conf[1]['keyID'], url, pr_key1, token1)
    set_apla_consensus(conf[2]['keyID'], url, pr_key1, token1)
    set_apla_consensus(conf[0]['keyID'], url, pr_key1, token1)
    
    print("Start create voting 1")
    
    data = actions.login(url, pr_key2, 3)
    token2 = data["jwtToken"]
    create_voiting(conf[1]["tcp_address"], conf[1]["api_address"],
                   conf[1]["keyID"], conf[1]["pubKey"],
                   url, pr_key2, token2)
    voting_status_update(url, pr_key1, token1)

    data = actions.login(url, pr_key3, 3)
    token3 = data["jwtToken"]
    voiting(1, url, pr_key3, token3)
    data = actions.login(url, pr_key1, 3)
    token1 = data["jwtToken"]
    voiting(1, url, pr_key1, token1)
    data = actions.login(url, pr_key2, 3)
    token2 = data["jwtToken"]
    voiting(1, url, pr_key2, token2)
    
    print("Start create voting 2")
    data = actions.login(url, pr_key3, 3)
    token3 = data["jwtToken"]
    create_voiting(conf[2]["tcp_address"], conf[2]["api_address"],
                   conf[2]["keyID"], conf[2]["pubKey"],
                   url, pr_key3, token3)
    voting_status_update(url, pr_key1, token1)
    
    data = actions.login(url, pr_key3, 3)
    token3 = data["jwtToken"]
    voiting(2, url, pr_key3, token3)
    data = actions.login(url, pr_key1, 3)
    token1 = data["jwtToken"]
    voiting(2, url, pr_key1, token1)
    data = actions.login(url, pr_key2, 3)
    token2 = data["jwtToken"]
    if voiting(2, url, pr_key2, token2) == True:
        print("Nodes successfully linked")
        exit(0)