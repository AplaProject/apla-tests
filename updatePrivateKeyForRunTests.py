import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-privateKeyPath', default='D:\\genesis-go')
parser.add_argument('-configPath', default='D:\\GitHub\\GenesisKernel\\genesis-tests\\')
parser.add_argument('-dbName', default='gen1')
args = parser.parse_args()

with open(os.path.join(args.privateKeyPath, 'PrivateKey'), 'r') as f:
	privKey1 = f.read()

file = os.path.join(args.configPath, "hostConfig.json")
with open(file, 'r') as f:
	data = f.read()
	lines = json.loads(data)

# Update private keys in config
lines["1"]["private_key"] = privKey1
lines["2"]["private_key"] = privKey1
lines["3"]["private_key"] = privKey1

# Update url in config
lines["2"]["url"] = lines["1"]["url"]
lines["3"]["url"] = lines["1"]["url"]

# Update DB name in config
lines["1"]["dbName"] = args.dbName
lines["2"]["dbName"] = args.dbName
lines["3"]["dbName"] = args.dbName

with open(file, 'w') as f:
	json.dump(lines, f)

print("hostConfig.json is updated!")