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

def getKeys():
	path = os.path.join(os.getcwd(), "fixtures", "prKeys.json")
	with open(path, 'r') as f:
		data = f.read()
	return json.loads(data)

def readFixtures(type):
	path = ""
	if type == "contracts":
		path = os.path.join(os.getcwd(), "fixtures", "contracts.json")
	if type == "pages":
		path = os.path.join(os.getcwd(), "fixtures", "pages.json")
	with open(path, 'r', encoding='UTF-8') as f:
		data = f.read()
	return json.loads(data)
