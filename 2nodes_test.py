import subprocess
import signal
import time
import os
import ctypes
import json
import utils

workDir1 = 'D:\\apla-go'
workDir2 = 'D:\\apla2'
testsDir = 'D:\\apla\\apla-tests'
binDir = 'C:\\MyGo\\bin\\go-apla.exe'
dbName1 = 'aplafront'
dbName2 = 'apla2'
dbPass = 'postgres'
dbLogin = 'postgres'
PIPE = subprocess.PIPE
start1node1 = 'start '+binDir+' -workDir='+workDir1+' -initConfig=1 -tcpPort=7078 -httpPort=7079 -configPath=NUL -initDatabase=1 -generateFirstBlock=1 -dbHost=localhost -dbPort=5432 -dbName='+dbName1+' -dbUser='+dbLogin+' -dbPassword='+dbPass+' -firstBlockPath=' + workDir1 +'\\1block'
node1 = subprocess.Popen(start1node1, shell = True)
node1.wait()
print(node1.pid)
time.sleep(10)
start1node2 = 'start '+binDir+' -workDir='+workDir2+' -initConfig=1 -configPath=NUL -tcpPort=7081 -httpPort=7018 -initDatabase=1 -dbHost=localhost -dbPort=5432 -dbName='+dbName2+' -dbUser='+dbLogin+' -dbPassword='+dbPass+' -generateFirstBlock=1'
node2 = subprocess.Popen(start1node2, shell = True)
node2.wait()
time.sleep(20)
print(node2.pid)
with open(workDir2+'\\apla.pid', 'r') as f:
	data = f.read()
js = json.loads(data)
print(js)
id = int(js["pid"])
print(js["pid"])
subprocess.Popen("taskkill /F /T /PID %i"%id, shell=True)
time.sleep(10)
updater = subprocess.Popen('python '+testsDir+'\\updateFullNodes.py', shell=True)
updater.wait()
time.sleep(10)
with open(workDir2+'\\KeyID', 'r') as f:
	keyID2 = f.read()
print(keyID2)
start2node2 = 'start '+binDir+' -workDir='+workDir2+' -tcpPort=7081 -httpPort=7018 -dbHost=localhost -dbPort=5432 -dbName='+dbName2+' -dbUser='+dbLogin+' -dbPassword='+dbPass+' -initDatabase=1 -firstBlockPath='+workDir1+'\\1block -keyID=' + keyID2
node2 = subprocess.Popen(start2node2, shell = True)
time.sleep(25)
countDBstart = utils.getCountDBObjects("localhost", dbName2, dbLogin, dbPass)
with open(workDir1+'\\PrivateKey', 'r') as prfile:
	prKey = prfile.read()
with open(testsDir+'\\config.json') as fconf:
	lines = fconf.readlines()
del lines[2]
lines.insert(2, "\"private_key\": \""+prKey+"\",\n")
with open(testsDir+'\\config.json', 'w') as fconf:
	fconf.write(''.join(lines))
time.sleep(5)
tests = subprocess.Popen('python '+testsDir+'\\tests_API.py', shell = True)
tests.wait()
if utils.compare_keys_cout("localhost", dbName2, dbLogin, dbPass):
	print("Block_chain is OK")
else:
	print("Error: There are different count of keys in block_chain")
utils.get_ten_items("localhost", dbName1, dbLogin, dbPass)
utils.get_ten_items("localhost", dbName2, dbLogin, dbPass)
with open(workDir2+'\\apla.pid', 'r') as f:
	data2 = f.read()
js2 = json.loads(data2)
print(js2)
id2 = int(js2["pid"])
print(js2["pid"])
subprocess.Popen("taskkill /F /T /PID %i"%id2, shell=True)
time.sleep(10)
countDBapla2 = utils.getCountDBObjects("localhost", dbName2, dbLogin, dbPass)
countDBapla1 = utils.getCountDBObjects("localhost", dbName1, dbLogin, dbPass)
if countDBapla2["tables"] != countDBapla1["tables"]:
	print("Error: Comapare! There are different count of Tables in tables of nodes!")
if countDBapla2["contracts"] != countDBapla1["contracts"]:
	print("Error: Comapare!! There are different count of Contracts in tables of nodes!")
if countDBapla2["pages"] != countDBapla1["pages"]:
	print("Error: Comapare!! There are different count of pages in tables of nodes!")
if countDBapla2["menus"] != countDBapla1["menus"]:
	print("Error: Comapare!! There are different count of menus in tables of nodes!")
if countDBapla2["blocks"] != countDBapla1["blocks"]:
	print("Error: Comapare!! There are different count of blocks in tables of nodes!")
if countDBapla2["params"] != countDBapla1["params"]:
	print("Error: Comapare!! There are different count of params in tables of nodes!")
if countDBapla2["locals"] != countDBapla1["locals"]:
	print("Error: Comapare!! There are different count of locals in tables of nodes!") 




