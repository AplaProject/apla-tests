import json
import os


def readMainConfig():
	path = os.path.join(os.getcwd(), "config.json")
	with open(path, 'r') as f:
		data = f.read()
	return json.loads(data)


def getNodeConfig():
	path = os.path.join(os.getcwd(), "hostConfig.json")
	with open(path, 'r') as f:
		data = f.read()
	return json.loads(data)


def readFixtures(type):
	path = ""
	if type == "contracts":
		path = os.path.join(os.getcwd(), "fixtures", "contracts.json")
	with open(path, 'r') as f:
		data = f.read()
	return json.loads(data)
