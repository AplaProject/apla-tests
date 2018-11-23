import subprocess
import time
import os
import json
import argparse
import shutil
import sys
module_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.split(module_dir)[0]
libs_path = os.path.join(libs_dir, 'libs')
sys.path.insert(0, libs_path)
import loger


log = loger.create_loger(__name__, 'environment.log')
log.info('Start ' + __file__)

curDir = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()

parser.add_argument('-action', required=True)
parser.add_argument('-binary', required=True)
parser.add_argument('-workDir', default=os.path.join(curDir, 'data'))

parser.add_argument('-dbHost', default='localhost')
parser.add_argument('-dbPort', default='5432')
parser.add_argument('-dbUser', default='postgres')
parser.add_argument('-dbPassword', default='postgres')

parser.add_argument('-tcpPort', default='7077')
parser.add_argument('-httpPort', default='7076')
parser.add_argument('-dbName', default='gen4')

parser.add_argument('-test', default='true')
parser.add_argument('-wait', default='3')


args = parser.parse_args()

wait = int(args.wait)

binary = os.path.abspath(args.binary)
workDir = os.path.abspath(args.workDir)
dataDir = os.path.join(workDir, 'node' + args.tcpPort)
firstBlockPath = os.path.join(workDir, '1block')

log.error(args.action)

if args.action == "create":
	os.makedirs(dataDir)
	log.error('Work dirs created')
	generateConfig = subprocess.Popen([
		binary,
		'config',
		'--dataDir='+dataDir,
		'--firstBlock='+firstBlockPath,
		'--dbName='+args.dbName,
		'--tcpPort='+args.tcpPort,
		'--httpPort='+args.httpPort,
		'--dbPassword='+args.dbPassword,
		'--nodesAddr='+'127.0.0.1:7078'
	])
	log.info('Generated config for second node')
	time.sleep(wait)

	# Generate keys for second node
	generateKeys = subprocess.Popen([
		binary,
		'generateKeys',
		'--config='+dataDir+'/config.toml'
	])
	log.info('Generated keys for second node')
	time.sleep(wait)

	# Init database
	startFirstNode = subprocess.Popen([
		binary,
		'initDatabase',
		'--config='+dataDir+'/config.toml'
	])
	log.info('DB for second node is initialized')
	time.sleep(wait)
	with open(os.path.join(dataDir, 'PrivateKey'), 'r') as f:
		priv_key = f.read()
	with open(os.path.join(dataDir, 'PublicKey'), 'r') as f:
		pubKey = f.read()
	with open(os.path.join(dataDir, 'KeyID'), 'r') as f:
		key_id = f.read()
	with open(os.path.join(dataDir, 'NodePublicKey'), 'r') as f:
		node_pub_key = f.read()
		
	new_node = {'url': 'http://localhost:' + args.httpPort + '/api/v2',
			'private_key': priv_key, 'keyID': key_id,'pubKey': node_pub_key,
        	'tcp_address': 'localhost:' + args.tcpPort,
         	'api_address': 'http://localhost:' + args.httpPort,
          	'db': {'dbHost': args.dbHost, 'dbName': args.dbName,
					'login': args.dbUser, 'pass': args.dbPassword}}
	resultFile = os.path.join(curDir + '/../', '101nodes.json')
	with open(resultFile, 'r') as f:
		data = f.read()
	old_nodes = json.loads(data)
	old_nodes.append(new_node)
	with open(resultFile, 'w') as fconf:
		fconf.write(json.dumps(old_nodes, indent=4))
	
	
#start node
if args.action == "start":
	# Start third node
	startFirstNode = subprocess.Popen([
		binary,
		'start',
		'--config='+dataDir+'/config.toml'
	])
	log.info('Third node started')
	time.sleep(wait)

log.error('Nodes successfully started')
