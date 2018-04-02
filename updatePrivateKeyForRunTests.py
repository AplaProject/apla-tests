import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-privateKeyPath', default='D:\\genesis-go')
parser.add_argument('-configPath', default='D:\\GitHub\\GenesisKernel\\genesis-tests\\')
parser.add_argument('-dbName', default='gen1')
args = parser.parse_args()

with open(os.path.join(args.privateKeyPath, 'PrivateKey'), 'r') as f:
	privKey1 = f.read()

config = os.path.join(args.configPath, 'config.json')
with open(config) as fconf:
	lines = fconf.readlines()

# Update private keys in config
del lines[2]
lines.insert(2, " \"private_key\": \""+privKey1+"\",\n")

del lines[5]
lines.insert(5, " \"dbName\": \""+args.dbName+"\",\n")
with open(config, 'w') as fconf:
	fconf.write(''.join(lines))

print("PrivateKey is updated!")


