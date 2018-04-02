import subprocess
import signal
import time
import os
import ctypes
import json
import argparse
import shutil

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

parser.add_argument('-gapBetweenBlocks', default='2')
parser.add_argument('-centrifugo', required=True)

args = parser.parse_args()

binary = os.path.abspath(args.binary)
workDir = os.path.abspath(args.workDir)
workDir1 = os.path.join(workDir, 'node1')
workDir2 = os.path.join(workDir, 'node2')
firstBlockPath = os.path.join(workDir, '1block')

if os.path.exists(workDir):
	shutil.rmtree(workDir)
os.makedirs(workDir1)
os.makedirs(workDir2)

# Create config for centrifugo
cenConfig = os.path.join(args.centrifugo, "config.json")
linesC = []
linesC.insert(0, "{\n")
linesC.insert(1, "\"secret\": \"4597e75c-4376-42a6-8c1f-7e3fc7eb2114\",\n")
linesC.insert(2, "\"admin_secret\": \"admin\"\n")
linesC.insert(3, "}")
with open(cenConfig, 'w') as fconf:
	fconf.write(''.join(linesC))
	
# Run centrifugo
cenPath = os.path.join(args.centrifugo, "centrifugo")
centrifugo = subprocess.Popen([
	cenPath,
	'--config=config.json',
	'--admin',
	'--insecure_admin',
	'--web'
])
time.sleep(5)

# Generate config for first node
config1 = subprocess.Popen([
	binary,
	'config',
	'--dataDir='+workDir1,
	'--firstBlock='+firstBlockPath,
	'--dbName='+args.dbName1
])
time.sleep(10)

#Update config for first node
configPath = os.path.join(workDir1, 'config.toml')
with open(configPath) as fconf:
	lines = fconf.readlines()
del lines[24]
lines.insert(24, "  Password = \""+args.dbPassword+"\"\n")
del lines[32]
lines.insert(32, "  Secret = \"4597e75c-4376-42a6-8c1f-7e3fc7eb2114\"\n")
del lines[33]
lines.insert(33, "URL = \"http://127.0.0.1:8000\"\n")
with open(configPath, 'w') as fconf:
	fconf.write(''.join(lines))

#Generate keys for first block
keys1 = subprocess.Popen([
	binary,
	'generateKeys',
	'--config='+workDir1+'/config.toml'
])
time.sleep(10)

#Generate first block
firstBlock = subprocess.Popen([
	binary,
	'generateFirstBlock',
	'--config='+workDir1+'/config.toml'
])
time.sleep(10)

#Init data base
firstBlock = subprocess.Popen([
	binary,
	'initDatabase',
	'--config='+workDir1+'/config.toml'
])
time.sleep(10)

#Start first node
startFirstNode = subprocess.Popen([
	binary,
	'start',
	'--config='+workDir1+'/config.toml'
])
time.sleep(10)

#Generate config for second node
generateConfig2 = subprocess.Popen([
	binary,
	'config',
	'--dataDir='+workDir2,
	'--firstBlock='+firstBlockPath,
	'--dbName='+args.dbName2,
	'--tcpPort='+args.tcpPort2,
	'--httpPort='+args.httpPort2,
	'--nodesAddr='+"127.0.0.1:"+args.tcpPort1
])
time.sleep(10)

#Update config for second node
configPath = os.path.join(workDir2, 'config.toml')
with open(configPath) as fconf:
	lines = fconf.readlines()
del lines[24]
lines.insert(24, "  Password = \""+args.dbPassword+"\"\n")
del lines[32]
lines.insert(32, "  Secret = \"4597e75c-4376-42a6-8c1f-7e3fc7eb2114\"\n")
del lines[33]
lines.insert(33, "URL = \"http://127.0.0.1:8000\"\n")
with open(configPath, 'w') as fconf:
	fconf.write(''.join(lines))

#Generate keys for second node
generateKeys = subprocess.Popen([
	binary,
	'generateKeys',
	'--config='+workDir2+'/config.toml'
])
time.sleep(10)

with open(os.path.join(workDir1, 'PrivateKey'), 'r') as f:
	privKey1 = f.read()
with open(os.path.join(workDir2, 'PrivateKey'), 'r') as f:
	privKey2 = f.read()
with open(os.path.join(workDir1, 'KeyID'), 'r') as f:
	keyID1 = f.read()
with open(os.path.join(workDir1, 'NodePublicKey'), 'r') as f:
	nodePubKey1 = f.read()
with open(os.path.join(workDir2, 'KeyID'), 'r') as f:
	keyID2 = f.read()
with open(os.path.join(workDir2, 'NodePublicKey'), 'r') as f:
	nodePubKey2 = f.read()
with open(os.path.join(workDir2, 'PublicKey'), 'r') as f:
	pubKey2 = f.read()

print('Update keys')
code = subprocess.call([
	'python',
	os.path.join(curDir, 'updateKeys.py'),
	privKey1,
	'127.0.0.1',
	args.httpPort1,
	keyID2,
	pubKey2,
	'100000000',
])
if code != 0:
	print("Error update keys")
	node1.kill()
	exit(1)

print('Update full_nodes')
# generate full_nodes string
host = '127.0.0.1'

flString1 = "[\""+host+":"+args.tcpPort1+"\",\"http://"+host+":"+args.httpPort1+"\",\""+keyID1+"\",\""+nodePubKey1+"\"]"
flString2 = "[\""+host+":"+args.tcpPort2+"\",\"http://"+host+":"+args.httpPort2+"\",\""+keyID2+"\",\""+nodePubKey2+"\"]"

newVal = "[" + flString1 + "," + flString2 + "]"
print(newVal)
print('Update full_nodes')
code = subprocess.call([
	'python',
	os.path.join(curDir, 'newValToFullNodes.py'),
	privKey1,
	'127.0.0.1',
	args.httpPort1,
	newVal
])
if code != 0:
	print("Error update full_nodes")
	node1.kill()
	exit(1)

print('Update gap_between_blocks')
code = subprocess.call([
	'python',
	os.path.join(curDir, 'updateSysParam.py'),
	'-httpHost=127.0.0.1',
	'-httpPort='+args.httpPort1,
	'-privKey='+privKey1,
	'-name=gap_between_blocks',
	'-value='+args.gapBetweenBlocks
])
if code != 0:
	print("Error update gap_between_blocks")
	node1.kill()
	exit(1)

time.sleep(20)

#Init database
startFirstNode = subprocess.Popen([
	binary,
	'initDatabase',
	'--config='+workDir2+'/config.toml'
])
time.sleep(10) 

#Start second node
startFirstNode = subprocess.Popen([
	binary,
	'start',
	'--config='+workDir2+'/config.toml'
])
time.sleep(10)

# Update config for tests
config = os.path.join(curDir+ '/../', 'hostConfig.json')
with open(config) as fconf:
 lines = fconf.readlines()

# Update URLs in config
del lines[3]
lines.insert(3, "\t\t\"url\": \"""http://localhost:"+args.httpPort1+"/api/v2" + "\",\n")
del lines[13]
lines.insert(13, "\t\t\"url\": \"""http://localhost:"+args.httpPort2+"/api/v2" + "\",\n")

# Update DB names in config
del lines[6]
lines.insert(6, "\t\t\"dbName\": \""+args.dbName1+"\",\n")
del lines[16]
lines.insert(16, "\t\t\"dbName\": \""+args.dbName2+"\",\n")

# Update private keys in config
del lines[4]
lines.insert(4, "\t\t\"private_key\": \""+privKey1+"\",\n")
del lines[14]
lines.insert(14, "\t\t\"private_key\": \""+privKey2+"\",\n")
with open(config, 'w') as fconf:
 fconf.write(''.join(lines))


