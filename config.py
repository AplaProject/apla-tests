import json



def readMainConfig():
	with open('.\config.json', 'r') as f:
		data = f.read()
	return json.loads(data)

def getNodeConfig(nodeNum):
    with open('.\hostConfig.json', 'r') as f:
        data = f.read()
    return json.loads(data)
