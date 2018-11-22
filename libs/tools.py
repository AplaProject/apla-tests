import os
import json
import random
import string
import yaml


def generate_random_name():
    name = []
    for _ in range(1, 30):
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
    if type == 'main':
        path = os.path.join(os.getcwd(), 'config.json')
    if type == 'nodes':
        path = os.path.join(os.getcwd(), 'nodesConfig.json')
    if type == 'test':
        path = os.path.join(os.getcwd(), 'testConfig.json')
    with open(path, 'r') as f:
        data = f.read()
    return json.loads(data)


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
