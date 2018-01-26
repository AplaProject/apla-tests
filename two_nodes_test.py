import subprocess
import signal
import time
import os
import ctypes
import json
import utils
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
parser.add_argument('-dbName1', default='apla')

parser.add_argument('-tcpPort2', default='7081')
parser.add_argument('-httpPort2', default='7018')
parser.add_argument('-dbName2', default='apla2')

parser.add_argument('-gapBetweenBlocks', default='10')

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

# Start first node
utils.clear_db(args.dbHost, args.dbName1, args.dbUser, args.dbPassword)
node1 = subprocess.Popen([
	binary,
	'-workDir='+workDir1,
	'-initConfig=1',
	'-configPath='+os.devnull,
	'-tcpPort='+args.tcpPort1,
	'-httpPort='+args.httpPort1,
	'-initDatabase=1',
	'-dbHost='+args.dbHost,
	'-dbPort='+args.dbPort,
	'-dbName='+args.dbName1,
	'-dbUser='+args.dbUser,
	'-dbPassword='+args.dbPassword,
	'-generateFirstBlock=1',
	'-firstBlockPath='+firstBlockPath
])
if not utils.wait_db_ready(args.dbHost, args.dbName1, args.dbUser, args.dbPassword):
	print("Error init db1")
	node1.kill()
	exit(1)

# Init second node
code = subprocess.call([
	binary,
	'-workDir='+workDir2,
	'-initConfig=1',
	'-configPath='+os.devnull,
	'-tcpPort='+args.tcpPort2,
	'-httpPort='+args.httpPort2,
	'-initDatabase=1',
	'-dbHost='+args.dbHost,
	'-dbPort='+args.dbPort,
	'-dbName='+args.dbName2,
	'-dbUser='+args.dbUser,
	'-dbPassword='+args.dbPassword,
	'-generateFirstBlock=1',
	'-firstBlockPath='+os.devnull,
	'-noStart=1'
])
if code != 0:
	print("Error init node2")
	node1.kill()
	exit(1)

with open(os.path.join(workDir1, 'PrivateKey'), 'r') as f:
	privKey1 = f.read()
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
code = subprocess.call([
	'python',
	os.path.join(curDir, 'updateFullNode.py'),
	privKey1,
	keyID1,
	nodePubKey1,
	keyID2,
	nodePubKey2,
	'127.0.0.1',
	args.httpPort1,
	'127.0.0.1',
	args.tcpPort2
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

# Start second node
utils.clear_db(args.dbHost, args.dbName2, args.dbUser, args.dbPassword)
node2 = subprocess.Popen([
	binary,
	'-workDir='+workDir2,
	'-tcpPort='+args.tcpPort2,
	'-httpPort='+args.httpPort2,
	'-initDatabase=1',
	'-dbHost='+args.dbHost,
	'-dbPort='+args.dbPort,
	'-dbName='+args.dbName2,
	'-dbUser='+args.dbUser,
	'-dbPassword='+args.dbPassword,
	'-firstBlockPath='+firstBlockPath,
	'-keyID='+keyID2
])

if not utils.wait_db_ready(args.dbHost, args.dbName2, args.dbUser, args.dbPassword, data={"tables":32, "blocks":5}):
	print("Error init db2")
	node1.kill()
	node2.kill()
	exit(1)

# Update config
configPath = os.path.join(curDir, 'config.json')
with open(configPath) as fconf:
	lines = fconf.readlines()
del lines[2]
lines.insert(2, "\"private_key\": \""+privKey1+"\",\n")
with open(configPath, 'w') as fconf:
	fconf.write(''.join(lines))

code = subprocess.call([
	'python',
	os.path.join(curDir, 'block_chain_test.py'),
	'-dbHost='+args.dbHost,
	'-dbUser='+args.dbUser,
	'-dbPassword='+args.dbPassword,
	'-dbName1='+args.dbName1,
	'-dbName2='+args.dbName2,
	'-sleep='+args.gapBetweenBlocks
])

node1.kill()
node2.kill()

if code != 0:
	print("Error block chain test")
	exit(1)
