import time
import json

from libs import actions, tools, loger


log = loger.create_loger(__name__, 'environment.log')


def is_in_block(call, url, token):
    status = actions.tx_status(url, 30, call, token)
    if "blockid" not in status or int(status["blockid"]) < 0:
        return False
    return True


def roles_install(url, pr_key, token):
    data = {}
    log.info("RolesInstall started")
    call = actions.call_contract(url, pr_key, "RolesInstall",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("RolesInstall is failed")
        exit(1)


def voting_templates_install(url, pr_key, token):
    data = {}
    log.info("VotingTemplatesInstall started")
    call = actions.call_contract(url, pr_key, "VotingTemplatesInstall",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("VotingTemplatesInstall is failed")
        exit(1)


def edit_app_param(name, val, url, pr_key, token):
    log.info("EditAppParam started")
    id = actions.get_object_id(url, name, "app_params", token)
    data = {"Id": id, "Value": val, "Conditions": "true"}
    call = actions.call_contract(url, pr_key, "EditAppParam",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("EditAppParam " + name + " is failed")
        exit(1)


def update_profile(name, url, pr_key, token):
    log.info("UpdateProfile started")
    time.sleep(5)
    data = {"member_name": name}
    resp = actions.call_contract(url, pr_key, "ProfileEdit",
                                 data, token)
    if not is_in_block(resp, url, token):
        log.error("UpdateProfile " + name + " is failed")
        exit(1)


def set_apla_consensus(id, url, pr_key, token):
    log.info("setAplaconsensus started")
    data = {"member_id": id, "rid": 3}
    call = actions.call_contract(url, pr_key, "RolesAssign",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("RolesAssign " + id + " is failed")
        exit(1)


def create_voiting(tcp_address, api_address, key_id, pub_key, url, pr_key, token):
    log.info("VotingNodeAdd started")
    data = {"TcpAddress": tcp_address, "ApiAddress": api_address,
            "KeyId": key_id, "PubKey": pub_key, "Duration": 1}
    call = actions.call_contract(url, pr_key, "VotingNodeAdd",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("VotingNodeAdd is failed")
        exit(1)


def voting_status_update(url, pr_key, token):
    log.info("VotingStatusUpdate started")
    data = {}
    call = actions.call_contract(url, pr_key, "VotingStatusUpdate",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("VoitingStatusUpdate is failed")
        exit(1)


def voiting(id, url, pr_key, token):
    log.info("VotingDecisionAccept started")
    data = {"votingID": id,
            "RoleId": 3}
    call = actions.call_contract(url, pr_key, "VotingDecisionAccept",
                                 data, token)
    if not is_in_block(call, url, token):
        log.error("VotingDecisionAccept " + id + " is failed")
        exit(1)
        return False
    return True


if __name__ == "__main__":
    log.info('Start ' + __name__)
    conf = tools.read_config("nodes")
    url = conf[0]["url"]
    pr_key1 = conf[0]['private_key']
    pr_key2 = conf[1]['private_key']
    pr_key3 = conf[2]['private_key']
    data = actions.login(url, pr_key1, 0)
    token1 = data["jwtToken"]
    actions.imp_app("system", url, pr_key1, token1)
    actions.imp_app("conditions", url, pr_key1, token1)
    actions.imp_app("basic", url, pr_key1, token1)
    actions.imp_app("lang_res", url, pr_key1, token1)

    roles_install(url, pr_key1, token1)

    voting_templates_install(url, pr_key1, token1)
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

    log.info("Start create voting 1")
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

    log.info("Start create voting 2")
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
    if voiting(2, url, pr_key2, token2):
        log.info("Nodes successfully linked")
        exit(0)
    else:
        log.error("Nodes is not linked")
        exit(1)
