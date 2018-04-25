import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-privateKeyPath', default='D:\\genesis-go')
parser.add_argument('-configPath', default='D:\\GitHub\\GenesisKernel\\genesis-tests\\')
parser.add_argument('-dbName', default='gen1')
args = parser.parse_args()

with open(os.path.join(args.privateKeyPath, 'PrivateKey'), 'r') as f:
	privKey1 = f.read()

config = os.path.join(args.configPath, 'hostConfig.json')
with open(config) as fconf:
	lines = fconf.readlines()

# Update private keys in hostConfig
del lines[4]
lines.insert(4, "\t\t\"private_key\": \""+privKey1+"\",\n")
del lines[15]
lines.insert(15, "\t\t\"private_key\": \""+privKey1+"\",\n")

# Update db name in hostConfig
del lines[7]
lines.insert(7, "\t\t\"dbName\": \""+args.dbName+"\",\n")
del lines[18]
lines.insert(18, "\t\t\"dbName\": \""+args.dbName+"\",\n")

# Update url 2 in hostConfig
del lines[14]
lines.insert(14, lines[3])

with open(config, 'w') as fconf:
	fconf.write(''.join(lines))

print("hostConfig is updated!")


