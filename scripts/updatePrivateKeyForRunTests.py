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

# Update private keys in config
del lines[4]
lines.insert(4, "\t\t\"private_key\": \""+privKey1+"\",\n")
del lines[15]
lines.insert(15, "\t\t\"private_key\": \""+privKey1+"\",\n")
del lines[26]
lines.insert(26, "\t\t\"private_key\": \""+privKey1+"\",\n")

# Update url in config
del lines[14]
lines.insert(14, lines[3])
del lines[25]
lines.insert(25, lines[3])

# Update DB name in config
del lines[7]
lines.insert(7, "\t\t\"dbName\": \""+args.dbName+"\",\n")
del lines[18]
lines.insert(18, "\t\t\"dbName\": \""+args.dbName+"\",\n")
del lines[29]
lines.insert(29, "\t\t\"dbName\": \""+args.dbName+"\",\n")


with open(config, 'w') as fconf:
	fconf.write(''.join(lines))

print("hostConfig.json is updated!")


