import subprocess
import time
import os
import json
import argparse
import shutil
import sys

from libs import loger, actions, tools, check

qurum = {"3": 3, "4": 4, "5": 5, "6": 5, "7": 6, "8": 7, "9": 7, "10": 8, "11": 9, "12": 10,
         "13":10, "14": 11, "15": 12, "16": 12, "17": 13, "18": 14, "19": 14, "20": 15, "21":16,
         "22": 17, "23": 17, "24": 18, "25": 18, "26": 19, "27": 20, "28": 21, "29":21, "30": 22,
         "31": 23, "32": 24, "33": 24, "34": 25, "35":26, "36": 27, "37": 27, "38": 28, "39": 29,
         "40": 28, "41": 29, "42": 29, "43": 30, "44": 31, "45": 31, "46": 32, "47": 33, "48":33,
         "49": 34, "50": 35, "51": 35, "52": 36, "53": 37, "54": 37, "55": 38, "56": 39, "57": 39,
         "58": 40, "59": 41, "60": 41, "61": 42, "62": 43, "63": 43, "64": 44, "65": 45, "66": 45,
         "67": 46, "68": 47, "69": 47, "70": 48, "71": 49, "72": 49, "73": 50, "74": 51, "75": 51,
         "76": 52, "77": 53, "78": 53, "79": 54, "80": 55, "81": 55, "82": 56, "83": 57, "84": 57,
         "85": 58, "86": 59, "87": 59, "88": 60, "89": 61, "90": 61, "91": 62, "92": 63, "93": 63,
         "94": 64, "95": 65, "96": 65, "97": 66, "98": 67, "99": 67, "100": 68, "101": 69}

log = loger.create_loger(__name__)
log.info('Start ' + __file__)

curDir = os.path.dirname(os.path.abspath(__file__))
confPath = os.path.join(curDir, 'nodesConfig.json')
resultFile = os.path.join(curDir, 'result.json')
parser = argparse.ArgumentParser()

parser.add_argument('-configFile', default=os.path.join(os.getcwd(), '101nodes.json'))
parser.add_argument('-threads', default=100)

args = parser.parse_args()

node_conf = tools.read_config('nodes')
wait = tools.read_config('test')['wait_upating_node']

data1 = actions.login(node_conf[0]['url'], node_conf[0]['private_key'], 0)
current = len(node_conf)-1
if str(node_conf[current]['tcp_address']) not in str(actions.get_sysparams_value(node_conf[0]['url'], data1['jwtToken'], "full_nodes")):
    print(node_conf[current]['tcp_address'])
    print(actions.get_sysparams_value(node_conf[0]['url'], data1['jwtToken'], "full_nodes"))
    print("last nodes wasn't linked")
    l_data0 = actions.login(node_conf[0]['url'], node_conf[current]['private_key'], 0)
    token0 = l_data0['jwtToken']
    print("founder balance: ", actions.get_balance_by_id(node_conf[0]['url'], token0, node_conf[0]['keyID']))
    actions.update_profile('nodeowner' + str(current), node_conf[0]['url'],
                           node_conf[current]['private_key'], token0, wait)
    actions.set_apla_consensus(node_conf[current]['keyID'], node_conf[0]['url'],
                               node_conf[0]['private_key'], data1['jwtToken'], wait)
    actions.create_voiting(node_conf[current]['tcp_address'], node_conf[current]['api_address'],
                   node_conf[current]['keyID'], node_conf[current]['pubKey'],
                   node_conf[0]['url'], node_conf[current]['private_key'], token0, wait)
    id_voting = actions.get_count(node_conf[0]['url'], 'votings', token0)
    actions.voting_status_update(node_conf[0]['url'], node_conf[0]['private_key'],
                                 data1['jwtToken'], wait)
    print('current', current)

    for a in range(0, current):
        print('a', a)
        data_cur = actions.login(node_conf[0]['url'], node_conf[a]['private_key'], 3)
        token_cur = data_cur['jwtToken']
        actions.voiting(id_voting, node_conf[0]['url'], node_conf[a]['private_key'],
                        token_cur, wait)
        if node_conf[current]['tcp_address'] in actions.get_sysparams_value(node_conf[0]['url'], data1['jwtToken'], "full_nodes"):
            break
    print(actions.get_sysparams_value(node_conf[0]['url'], token0, "full_nodes"))

with open(args.configFile, 'r') as f:
        data = f.read()
nodes = json.loads(data)
for i in range(current+1, len(nodes)-1):
#relocate new node parameters to nodesConfig.json
    with open(confPath, 'r') as f:
        data = f.read()
    currentNodes = json.loads(data)
    currentNodes.append(nodes[i])
    with open(confPath, 'w') as fconf:
        fconf.write(json.dumps(currentNodes, indent=4))
    node_conf = tools.read_config('nodes')

#compare_blocks
    time.sleep(30)
    print('i', i)
    data2 = actions.login(node_conf[i-1]['url'], node_conf[0]['private_key'], 0)
    max_block_id2 = actions.get_max_block_id(node_conf[i-1]['url'], data2['jwtToken'])
    res = actions.get_load_blocks_time(node_conf[0]['url'], data1['jwtToken'],
                                       max_block_id2, wait)
    current_res = {str(i):max_block_id2}
    #save monitoring file
    with open(resultFile, 'r') as f:
        data = f.read()
    result = json.loads(data)
    result.append(current_res)
    with open(resultFile, 'w') as fconf:
        fconf.write(json.dumps(result, indent=4))
    
#link new node to net
    print("url i-1: ", node_conf[i-1]['url']) 
    l_data0 = actions.login(node_conf[0]['url'], node_conf[i]['private_key'], 0)
    token0 = l_data0['jwtToken']
    print("founder balance: ", actions.get_balance_by_id(node_conf[0]['url'], token0, node_conf[0]['keyID']))
    actions.update_profile('nodeowner' + str(i), node_conf[0]['url'],
                           node_conf[i]['private_key'], token0, wait)
    actions.set_apla_consensus(node_conf[i]['keyID'], node_conf[0]['url'],
                               node_conf[0]['private_key'], data1['jwtToken'], wait)
    actions.create_voiting(node_conf[i]['tcp_address'], node_conf[i]['api_address'],
                   node_conf[i]['keyID'], node_conf[i]['pubKey'],
                   node_conf[0]['url'], node_conf[i]['private_key'], token0, wait)
    id_voting = actions.get_count(node_conf[0]['url'], 'votings', token0)
    actions.voting_status_update(node_conf[0]['url'], node_conf[0]['private_key'],
                                 data1['jwtToken'], wait)
    print('current', i)

    for j in range(0, len(node_conf)):
        print('j', j)
        print('i', i)
        data_cur = actions.login(node_conf[0]['url'], node_conf[j]['private_key'], 3)
        token_cur = data_cur['jwtToken']
        actions.voiting(id_voting, node_conf[0]['url'], node_conf[j]['private_key'],
                        token_cur, wait)
        print(node_conf[i]['tcp_address'])
        if str(node_conf[i]['tcp_address']) in str(actions.get_sysparams_value(node_conf[0]['url'], data1['jwtToken'], "full_nodes")):
            print("here")
            break
    print(actions.get_sysparams_value(node_conf[0]['url'], token0, "full_nodes"))
    

log.info('All nodes are started')
exit(0)
