import subprocess
import signal
import time
import os
import ctypes
import json
import argparse
import shutil
import sys

curDir = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()

parser.add_argument('-binary', required=True)
parser.add_argument('-workDir', default=os.path.join(curDir, 'data'))

parser.add_argument('-dbHost', default='localhost')
parser.add_argument('-dbPort', default='5432')
parser.add_argument('-dbUser', default='postgres')
parser.add_argument('-dbPassword', default='postgres')

parser.add_argument('-tcpPort1', default='7078')
parser.add_argument('-httpPort1', default='7079')
parser.add_argument('-dbName1', default='gen1')

parser.add_argument('-tcpPort2', default='7081')
parser.add_argument('-httpPort2', default='7018')
parser.add_argument('-dbName2', default='gen2')

parser.add_argument('-tcpPort3', default='7080')
parser.add_argument('-httpPort3', default='7082')
parser.add_argument('-dbName3', default='gen3')

parser.add_argument('-gapBetweenBlocks', default='2')
parser.add_argument('-centrifugo', required=True)
parser.add_argument('-test', default='true')

args = parser.parse_args()

binary = os.path.abspath(args.binary)
workDir = os.path.abspath(args.workDir)
workDir1 = os.path.join(workDir, 'node1')
workDir2 = os.path.join(workDir, 'node2')
workDir3 = os.path.join(workDir, 'node3')
firstBlockPath = os.path.join(workDir, '1block')


if os.path.exists(workDir):
	shutil.rmtree(workDir)
os.makedirs(workDir1)
os.makedirs(workDir2)
os.makedirs(workDir3)

# Set centrifugo variables
centrifugo_secret = '4597e75c-4376-42a6-8c1f-7e3fc7eb2114'
centrifugo_url = 'http://127.0.0.1:8000'
cenConfig = os.path.join(args.centrifugo, "config.json")
cenPath = os.path.join(args.centrifugo, "centrifugo")

# Create config for centrifugo
cen_config_string = {
	'secret': centrifugo_secret,
	'admin_secret': 'admin'
	}
with open(cenConfig, 'w') as cen_conf_file:
	json.dump(cen_config_string, cen_conf_file, indent=4)

# Run centrifugo
if sys.platform == 'win32':
	centrifugo = subprocess.Popen([
		cenPath,
		'--config='+cenConfig,
		'--admin',
		'--insecure_admin',
		'--web'
	])
else:
	centrifugo = subprocess.Popen([
		cenPath,
		'--config='+cenConfig,
		'--admin',
		'--admin_insecure'
	])

time.sleep(3)

# Generate config for first node
config1 = subprocess.Popen([
	binary,
	'config',
	'--dataDir='+workDir1,
	'--firstBlock='+firstBlockPath,
	'--dbPassword='+args.dbPassword,
	'--centUrl='+centrifugo_url,
	'--centSecret='+centrifugo_secret,
	'--dbName='+args.dbName1
])
time.sleep(3)

#Generate keys for first block
keys1 = subprocess.Popen([
	binary,
	'generateKeys',
	'--config='+workDir1+'/config.toml'
])
time.sleep(3)

#Generate first block
firstBlock = subprocess.Popen([
	binary,
	'generateFirstBlock',
	'--config='+workDir1+'/config.toml',
	'--test='+args.test
])
time.sleep(3)

#Init data base
firstBlock = subprocess.Popen([
	binary,
	'initDatabase',
	'--config='+workDir1+'/config.toml'
])
time.sleep(3)

#Start first node
startFirstNode = subprocess.Popen([
	binary,
	'start',
	'--config='+workDir1+'/config.toml'
])
time.sleep(3)

#Generate config for second node
generateConfig2 = subprocess.Popen([
	binary,
	'config',
	'--dataDir='+workDir2,
	'--firstBlock='+firstBlockPath,
	'--dbName='+args.dbName2,
	'--tcpPort='+args.tcpPort2,
	'--httpPort='+args.httpPort2,
	'--firstBlock='+firstBlockPath,
	'--dbPassword='+args.dbPassword,
	'--centUrl='+centrifugo_url,
	'--centSecret='+centrifugo_secret,
	'--nodesAddr='+"127.0.0.1:"+args.tcpPort1
])
time.sleep(3)

#Generate keys for second node
generateKeys = subprocess.Popen([
	binary,
	'generateKeys',
	'--config='+workDir2+'/config.toml'
])
time.sleep(3)

#Generate config for third node
generateConfig3 = subprocess.Popen([
	binary,
	'config',
	'--dataDir='+workDir3,
	'--firstBlock='+firstBlockPath,
	'--dbName=' + args.dbName3,
	'--tcpPort='+args.tcpPort3,
	'--httpPort='+args.httpPort3,
	'--firstBlock='+firstBlockPath,
	'--dbPassword='+args.dbPassword,
	'--centUrl='+centrifugo_url,
	'--centSecret='+centrifugo_secret,
	'--nodesAddr='+"127.0.0.1:"+args.tcpPort1
])
time.sleep(3)

#Generate keys for third node
generateKeys = subprocess.Popen([
	binary,
	'generateKeys',
	'--config='+workDir3+'/config.toml'
])
time.sleep(3)

#Init database
startFirstNode = subprocess.Popen([
	binary,
	'initDatabase',
	'--config='+workDir2+'/config.toml'
])
time.sleep(3) 

#Start third node
startFirstNode = subprocess.Popen([
	binary,
	'start',
	'--config='+workDir2+'/config.toml'
])
time.sleep(3)

#Init database
startThirdNode = subprocess.Popen([
	binary,
	'initDatabase',
	'--config='+workDir3+'/config.toml'
])
time.sleep(3) 

#Start third node
startThirdNode = subprocess.Popen([
	binary,
	'start',
	'--config='+workDir3+'/config.toml'
])
time.sleep(3)

with open(os.path.join(workDir1, 'PrivateKey'), 'r') as f:
	priv_key1 = f.read()
with open(os.path.join(workDir1, 'PublicKey'), 'r') as f:
	pubKey1 = f.read()
with open(os.path.join(workDir2, 'PrivateKey'), 'r') as f:
	priv_key2= f.read()
with open(os.path.join(workDir3, 'PrivateKey'), 'r') as f:
	priv_key3 = f.read()
with open(os.path.join(workDir1, 'KeyID'), 'r') as f:
	key_id1 = f.read()
with open(os.path.join(workDir1, 'NodePublicKey'), 'r') as f:
	node_pub_key1 = f.read()
with open(os.path.join(workDir2, 'KeyID'), 'r') as f:
	key_id2 = f.read()
with open(os.path.join(workDir2, 'NodePublicKey'), 'r') as f:
	node_pub_key2 = f.read()
with open(os.path.join(workDir2, 'PublicKey'), 'r') as f:
	pubKey2 = f.read()
with open(os.path.join(workDir3, 'KeyID'), 'r') as f:
	key_id3 = f.read()
with open(os.path.join(workDir3, 'NodePublicKey'), 'r') as f:
	node_pub_key3 = f.read()
with open(os.path.join(workDir3, 'PublicKey'), 'r') as f:
	pubKey3 = f.read()

	#-------------------------



	config = [
		{
			"url": "http://localhost:" + args.httpPort1 + "/api/v2",
			"private_key": priv_key1,
			"keyID": key_id1,
			"pubKey": node_pub_key1,
			"tcp_address": "localhost:" + args.tcpPort1,
			"api_address": "http://localhost:" + args.httpPort1,
			"db":
			{
				"dbHost": args.dbHost,
				"dbName": args.dbName1,
				"login": args.dbUser,
				"pass": args.dbPassword
				}
		},
		{
			"url": "http://localhost:" + args.httpPort2 + "/api/v2",
			"private_key": priv_key2,
			"keyID": key_id2,
			"pubKey": node_pub_key2,
			"tcp_address": "localhost:" + args.tcpPort2,
			"api_address": "http://localhost:" + args.httpPort2,
			"db":
			{
				"dbHost": args.dbHost,
				"dbName": args.dbName2,
				"login": args.dbUser,
				"pass": args.dbPassword
				}
		},
		{
			"url": "http://localhost:" + args.httpPort3 + "/api/v2",
			"private_key": priv_key3,
			"keyID": key_id3,
			"pubKey": node_pub_key3,
			"tcp_address": "localhost:" + args.tcpPort3,
			"api_address": "http://localhost:" + args.httpPort3,
			"db":
			{
				"dbHost": args.dbHost,
				"dbName": args.dbName3,
				"login": args.dbUser,
				"pass": args.dbPassword
			}
		}]

	# Update config for tests
confPath = os.path.join(curDir+ '/../', 'hostConfig.json')

with open(confPath, 'w') as fconf:
	fconf.write(json.dumps(config, indent=4))

print("Nodes successfully started")
