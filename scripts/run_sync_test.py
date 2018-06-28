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

parser.add_argument('-tcpPort3', default='7080')
parser.add_argument('-httpPort3', default='7082')
parser.add_argument('-dbName3', default='gen3')

parser.add_argument('-gapBetweenBlocks', default='2')
parser.add_argument('-centrifugo', required=True)

args = parser.parse_args()

# Run three nodes
threeNodes = subprocess.call([
	'python',
	'three_nodes_test.py',
	'-binary='+args.binary,
	'-dbName1='+args.dbName1,
	'-dbName2='+args.dbName2,
	'-dbName3='+args.dbName3,
	'-centrifugo='+args.centrifugo,
	'-dbUser='+args.dbUser,
	'-dbPassword='+args.dbPassword
])
if threeNodes != 0:
	print("Error threeNodes")

#Run locust
locust = subprocess.call([
	'locust',
	'--locustfile=locastfile.py',
	'--host=http://localhost:7018/api/v2',
	'--no-web',
	'--clients=50',
	'--hatch-rate=50',
	'--num-request=500'
])
if locust != 0:
	print("Error locust test")

#run checks
os.chdir("..")
test = subprocess.call([
	'python',
	'compare_nodes.py'
])
if test != 0:
	print("Error in compare nodes")