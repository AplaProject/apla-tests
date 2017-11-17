import json

def getConfig():
    with open('hostConfig.json', 'r') as f:
        data = f.read()
        conf = json.loads(data)
    return conf