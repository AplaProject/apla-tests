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

file = os.path.join(args.configPath, "config.json")
with open(file, 'r') as f:
	data = f.read()
	lines = json.loads(data)

# Update private keys in config
lines["private_key"] = privKey1

# Update DB name in config
lines["dbName"] = args.dbName

with open(file, 'w') as f:
	json.dump(lines, f, indent=4)

print("config.json is updated!")