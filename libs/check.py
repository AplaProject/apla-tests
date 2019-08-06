import unittest
import time
from libs import db, actions, loger, api, tools


log = loger.create_loger(__name__)
unit = unittest.TestCase()


def compare_nodes(config):
    nodes = len(config)
    wait_time = tools.read_config('test')['wait_sync']
    amounts = []
    data = []
    if actions.is_sync(config, wait_time, nodes):    
        i = 0
        while i < nodes:
            data = actions.login(config[i]['url'], config[i]['private_key'])
            token = data['jwtToken']
            amounts.append(actions.get_user_token_amounts(config[i]['url'], token))
            i += 1
        hash = []
        max_block = actions.get_max_block_id(config[0]['url'], token)
        i = 0
        while i < nodes:
            hash.append(db.get_blockchain_hash(config[i]['db'], max_block))
            i += 1
        node_position = db.compare_node_positions(
            config[0]['db'], max_block, nodes)
    
        main_dict = {'amounts': str(amounts[0]), 'hash': str(
            hash[0]), 'node_pos': 'True'}
        dict = []
        i = 0
        while i < nodes:
            dict.append({'amounts': str(amounts[i]), 'hash': str(hash[i]),
                         'node_pos': str(node_position)})
            if main_dict != dict[i]:
                print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                print('Error in node ' + str(i) + 'dict Main is ' + str(main_dict) +
                      ', current is ' + str(dict[i]))
                return False
            else:
                i += 1
        return True
    else:
        print("Nodes didn't downloads all blocks")
        return True


def is_tx_in_block(url, wait, tx, token):
    status = actions.tx_status(url, wait, tx['hash'], token)
    if status['blockid'] > 0:
        return status['blockid']
    else:
        msg = 'Transaction not in block. Status: ' + str(status)
        log.error(msg)
        unittest.TestCase.fail(msg)
        return None


def compare_db(config, url, token):
    nodes = len(config)
    dbInformation = []
    wait_time = tools.read_config('test')['wait_sync']
    if actions.is_sync(config, wait_time, nodes):
        first_db = actions.get_count_DB_objects(url, token)
        first_hashes = actions.get_table_hashes(url, token, config[0]['db'])
        i = 1
        while i < nodes:
            current_db = actions.get_count_DB_objects(url, token)
            current_hashes = actions.get_table_hashes(url, token, config[i]['db'])
            if current_db != first_db or current_hashes != first_hashes:
                print('Errorin db: Different info about ' + str(current_db) +
                      ' != ' + str(first_db) + ' current node is ' + str(i) +
                      'hashes: First: ' + str(first_hashes) + 'current: ' +
                      str(current_hashes))
                return False
            i += 1
        return True
    else:
        print("Nodes didn't downloads all blocks")
        return True


def is_new_key_in_keys(url, token, key_id, attempts, ecosystem=1):
    i = 0
    while i < attempts:
        keys_list = actions.get_list(url, 'keys', token)['list']
        for item in keys_list:
            if item['id'] == key_id \
                    and int(item['ecosystem']) == int(ecosystem):
                return True
        time.sleep(1)
        i += 1
    unittest.TestCase.fail('Key_id is not find in keys table.')
    return False

def cors(url, method):
    if api.cors(url, method):
        return True
    else:
        unittest.TestCase.fail('CORS is not allowed')
        return False
        
def is_updating(url):
    if not api.getuid(url):
        return True
    else:
        return False
    
def multi_tx_in_block(result, wait, url, jwt_token):
    result = actions.tx_status_multi(url, wait, result['hashes'], jwt_token)
    for status in result.values():
        if 'errmsg' in status:
            unittest.TestCase.fail('Transaction has error')
        if int(status['blockid']) < 0:
            unit.fail('BlockID not generated')