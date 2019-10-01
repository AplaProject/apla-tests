import os
import json
import random
import string
import yaml
import hashlib


def generate_random_name():
    name = []
    for _ in range(1, 30):
        sym = random.choice(string.ascii_lowercase)
        name.append(sym)
    return ''.join(name)

def generate_random_name_ch():
    name = []
    for i in range(1,6):
        for _ in ['abcdefghijklmnopqastuvwxyz']:
            sym = random.choice(string.ascii_lowercase)
            name.append(sym)
    return ''.join(name)


def generate_name_and_code(source_code):
    name = 'Cont_' + generate_random_name()
    code = generate_code(name, source_code)
    return code, name


def generate_code(contract_name, source_code):
    if not source_code:
        s_code = '{data { }    conditions { }    action { } }'
    else:
        s_code = source_code
    code = 'contract ' + contract_name + s_code
    return code


def read_config(type):
    path = ''
    if type == 'test':
        path1 = os.path.join(os.getcwd(), 'testConfig.json')
        path2 = os.path.join(os.getcwd(), 'testConfig.default.json')
        with open(path1, 'r') as f1:
            data1 = f1.read()
        conf = json.loads(data1)
        with open(path2, 'r') as f2:
            data2 = f2.read()
        conf_d = json.loads(data2)
        conf_d.update(conf)
        return conf_d
    else:
        if type == 'main':
            path = os.path.join(os.getcwd(), 'config.json')
        if type == 'nodes':
            path = os.path.join(os.getcwd(), 'nodesConfig.json')
        if type == 'nodes_ex':
            path = os.path.join(os.getcwd(), 'nodesConfig_ex.json')
        with open(path, 'r') as f:
            data = f.read()
        return json.loads(data)


def write_config(new_conf):
    path = os.path.join(os.getcwd(), 'testConfig.json')
    with open(path, 'w') as fconf:
        fconf.write(json.dumps(new_conf, indent=4))


def read_fixtures(type):
    path = ''
    if type == 'pages':
        path = os.path.join(os.getcwd(), 'fixtures', 'pages.json')
    if type == 'api':
        path = os.path.join(os.getcwd(), 'fixtures', 'api.json')
    if type == 'keys':
        path = os.path.join(os.getcwd(), 'fixtures', 'prKeys.json')
    with open(path, 'r', encoding='UTF-8') as f:
        data = f.read()
    return json.loads(data)


def read_fixtures_yaml(type):
    path = ''
    if type == 'contracts':
        path = os.path.join(os.getcwd(), 'fixtures', 'contracts.yaml')
    if type == 'simvolio':
        path = os.path.join(os.getcwd(), 'fixtures', 'simvolio.yaml')
    with open(path, 'r', encoding='UTF-8') as f:
        data = f.read()
    return yaml.load(data)


def generate_pr_key():
    return ''.join(random.choice('0123456789abcdef') for _ in range(64))


def get_hash_sha256(str_content):
    m = hashlib.sha256()
    m.update(bytes(str_content, 'utf-8'))
    return m.hexdigest()
