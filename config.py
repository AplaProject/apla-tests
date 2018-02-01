import json


def readMainConfig():
	with open('.\config.json', 'r') as f:
		data = f.read()
	return json.loads(data)


def getNodeConfig():
	with open('.\hostConfig.json', 'r') as f:
		data = f.read()
	return json.loads(data)


def readFixtures(type):
	path = ""
	if type == "contracts":
		path = '.\\fixtures\contracts.json'
	with open(path, 'r') as f:
		data = f.read()
	return json.loads(data)
