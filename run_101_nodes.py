import subprocess
import time
import os
import json
import argparse
import shutil
import sys

from libs import loger, actions, tools, check


log = loger.create_loger(__name__, 'environment.log')
log.info('Start ' + __file__)

curDir = os.path.dirname(os.path.abspath(__file__))
confPath = os.path.join(curDir, 'nodesConfig.json')
resultFile = os.path.join(curDir, 'result.json')
result = []
parser = argparse.ArgumentParser()

parser.add_argument('-configFile', default=os.path.join(os.getcwd(), '101nodes.json'))
parser.add_argument('-threads', default=100)

args = parser.parse_args()

with open(args.configFile, 'r') as f:
        data = f.read()
nodes = json.loads(data)
for node in nodes:
#relocate new node parameters to nodesConfig.json
    with open(confPath, 'r') as f:
        data = f.read()
    currentNodes = json.loads(data)
    currentNodes.append(node)
    with open(confPath, 'w') as fconf:
        fconf.write(json.dumps(currentNodes, indent=4))

#TODO run new node
    curDir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(curDir, 'scripts\\add_new_node.py')
    start_n = subprocess.Popen([
        'python',
        script_path,
        '-action=start',
        '-binary=D:\genesis\go-genesis.exe'
])
#compare_blocks
    node_conf = tools.read_config('nodes')
    wait = tools.read_config('test')['wait_upating_node']
    current = len(node_conf) - 1
    time.sleep(30)
    data2 = actions.login(node_conf[current]['url'], node_conf[0]['private_key'], 0)
    max_block_id2 = actions.get_max_block_id(node_conf[current]['url'], data2['jwtToken'])
    data1 = actions.login(node_conf[0]['url'], node_conf[0]['private_key'], 0)
    res = actions.get_load_blocks_time(node_conf[0]['url'], data1['jwtToken'],
                                       max_block_id2, wait)
    current_res = {str(current):max_block_id2}
    result.append(current_res)
    #save monitoring file
    with open(resultFile, 'w') as fconf:
        fconf.write(json.dumps(result, indent=4))
    
#link new node to net
    l_data0 = actions.login(node_conf[0]['url'], node_conf[current]['private_key'], 0)
    token0 = l_data0['jwtToken']
    
    actions.update_profile('nodeowner' + str(current), node_conf[0]['url'],
                           node_conf[current]['private_key'], token0, wait)
    actions.set_apla_consensus(node_conf[current]['keyID'], node_conf[0]['url'],
                               node_conf[0]['private_key'], data1['jwtToken'], wait)
    actions.create_voiting(node_conf[current]['tcp_address'], node_conf[current]['api_address'],
                   node_conf[current]['keyID'], node_conf[current]['pubKey'],
                   node_conf[0]['url'], node_conf[current]['private_key'], token0, wait)
    actions.voting_status_update(node_conf[0]['url'], node_conf[0]['private_key'],
                                 data1['jwtToken'], wait)
    for i in range(0, current):
        data_cur = actions.login(node_conf[0]['url'], node_conf[i]['private_key'], 3)
        token_cur = data_cur['jwtToken']
        actions.voiting(current, node_conf[0]['url'], node_conf[i]['private_key'],
                        token_cur, wait)
    
#run locust for new node 
    start_locust = subprocess.Popen("locust --locustfile=trx_load.py --host=" +\
                                     node_conf[0]['url'] + " --no-web --clients=" +\
                                     str(args.threads))


log.info('All nodes are started')
exit(0)