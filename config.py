import json


config = {}


def read():
	global config
	with open('config.json', 'r') as f:
		data = f.read()
		config = json.loads(data)
