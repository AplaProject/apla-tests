import os
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument('-configPath', required=True)
parser.add_argument('-privateKeyPath', required=True)
parser.add_argument('-url', default='http://localhost:7079/api/v2')
parser.add_argument('-dbHost', default='localhost')
parser.add_argument('-dbName', default='gen1')
parser.add_argument('-login', default='postgres')
parser.add_argument('-password', default='postgres')

args = parser.parse_args()


def get_private_key(filename):
    with open(os.path.join(args.privateKeyPath, filename), 'r') as f:
        return f.read()


def create_config(url, priv_key, db_host, db_name, login, password):
    config = {
        'url': url,
        'private_key': priv_key,
        'db': {
            'dbHost': db_host,
            'dbName': db_name,
            'login': login,
            'pass': password,
        }
    }
    with open(file, 'w') as f:
        f.write(json.dumps(config, indent=4))


if __name__ == '__main__':

    config_filename = 'config.json'
    file = os.path.join(args.configPath, config_filename)
    priv_key_path = os.path.join(args.privateKeyPath, 'PrivateKey')
    priv_key = get_private_key(priv_key_path)
    create_config(
        args.url,
        priv_key,
        args.dbHost,
        args.dbName,
        args.login,
        args.password,
    )
    print('{} is updated!'.format(config_filename))
