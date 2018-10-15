import os
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument('-privateKeyPath', required=True)
parser.add_argument('-configPath', required=True)
parser.add_argument('-dbName', required=True)
args = parser.parse_args()


def get_private_key(filename):
    with open(os.path.join(args.privateKeyPath, filename), 'r') as f:
        return f.read()


def read_nodes_config(file):
    with open(file, 'r') as f:
        data = f.read()
        return json.loads(data)


def change_nodes_config(lines, priv_key, db_name):
	# Update private keys in config
	lines['private_key'] = priv_key
	# Update DB name in config
	lines['db']['dbName'] = db_name


def save_nodes_config(file, lines):
    with open(file, 'w') as f:
        json.dump(lines, f, indent=4)


if __name__ == '__main__':

    config_filename = 'config.json'
    file = os.path.join(args.configPath, config_filename)
    priv_key_path = os.path.join(args.privateKeyPath, 'PrivateKey')
    lines = read_nodes_config(file)
    priv_key = get_private_key(priv_key_path)
    db_name = args.dbName
    change_nodes_config(lines, priv_key, db_name)
    save_nodes_config(file, lines)
    print('{} is updated!'.format(config_filename))
