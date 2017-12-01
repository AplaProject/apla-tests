import json


config = {}


def readMainConfig():
	with open('config.json', 'r') as f:
		data = f.read()
	global config
	config = json.loads(data)

def getNodeConfig(nodeNum):
    with open('hostConfig.json', 'r') as f:
        data = f.read()
    fullJ = json.loads(data)
    global config
    config = fullJ[nodeNum]
    
def getDBConfig():
	with open('dBconfig.json', 'r') as f:
		data = f.read()
	global config
	config = json.loads(data)