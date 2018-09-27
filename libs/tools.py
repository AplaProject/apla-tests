import os
import json
import random
import string

def json_to_list(js):
    fullList = []
    list = []
    for i in js:
        tup = ()
        list = []
        for element in i:
            list.append(i[element])
        tup = tuple(list)
        print("tup", tup)
        fullList.append(tup)
    print(fullList)
    return fullList


def generate_random_name():
    name = []
    for _ in range(1, 30):
        sym = random.choice(string.ascii_lowercase)
        name.append(sym)
    return "".join(name)

def generate_name_and_code(sourceCode):
    name = "Cont_" + generate_random_name()
    code = generate_code(name, sourceCode)
    return code, name

def generate_code(contractName, sourceCode):
    if sourceCode == "":
        sCode = """{data { }    conditions {    }    action {    }    }"""
    else:
        sCode = sourceCode
    code = "contract " + contractName + sCode
    return code


def read_config(type):
    path = ""
    if type == "main":
        path = os.path.join(os.getcwd(), "config.json")
    if type == "nodes":
        path = os.path.join(os.getcwd(), "nodesConfig.json")
    if type == "test":
        path = os.path.join(os.getcwd(), "testConfig.json")
    with open(path, 'r') as f:
        data = f.read()
    return json.loads(data)


def read_fixtures(type):
    path = ""
    if type == "contracts":
        path = os.path.join(os.getcwd(), "fixtures", "contracts.json")
    if type == "pages":
        path = os.path.join(os.getcwd(), "fixtures", "pages.json")
    if type == "api":
        path = os.path.join(os.getcwd(), "fixtures", "api.json")
    if type == "keys":
        path = os.path.join(os.getcwd(), "fixtures", "prKeys.json")
    if type == "simvolio":
        path = os.path.join(os.getcwd(), "fixtures", "simvolio.json")
    with open(path, 'r', encoding='UTF-8') as f:
        data = f.read()
    return json.loads(data)

