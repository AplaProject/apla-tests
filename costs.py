import unittest
import utils
import config
import requests
import json
import funcs
import os
import time
import argparse


def new_ecosystem(url, prKey, token, times):
    i = 1
    while i < times:
        data = {"Name": "Ecosys_" + utils.generate_random_name()}
        utils.call_contract(url, prKey,
                            "NewEcosystem", data, token)
        i = i + 1
        time.sleep(5)
            
def new_table(url, prKey, token, times):
    column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"},{"name":"Myb","type":"json",
        "index": "0",  "conditions":"true"}, {"name":"MyD","type":"datetime",
        "index": "0",  "conditions":"true"}, {"name":"MyM","type":"money",
        "index": "0",  "conditions":"true"},{"name":"MyT","type":"text",
        "index": "0",  "conditions":"true"}]"""
    permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
    i = 1
    while i < times:
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": column, "ApplicationId": 1, "Permissions": permission}
        utils.call_contract(url, prKey,
                                "NewTable", data, token)
        i = i + 1
        time.sleep(5)
            
def new_page(url, prKey, token, times):
    i = 1
    while i < times:
        data = {"Name": "Page_" + utils.generate_random_name(),
                    "Value": "Hello page!", "ApplicationId": 1,
                    "Conditions": "true", "Menu": "default_menu"}
        utils.call_contract(url, prKey,
                                "NewPage", data, token)
        i = i + 1
        time.sleep(5)

def new_contract(url, prKey, token, times):
    i = 1
    while i < times:
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        utils.call_contract(url, prKey,
                                "NewContract", data, token)
        i = i + 1
        time.sleep(5)

def edit_page(url, prKey, token, times):
    name = "Page_" + utils.generate_random_name()
    data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
    utils.call_contract(url, prKey,
                                "NewPage", data, token)
    status = utils.txstatus(url, 30, hash, token)
    if len(status['blockid']) > 0:
        i = 1
        while i < times:
            dataEdit = {"Id": funcs.get_count(url, "pages", token),
                    "Value": "Good by page!", "Conditions": "true",
                    "Menu": "default_menu"}
            utils.call_contract(url, prKey,
                                    "EditPage", dataEdit, token)
            i = i + 1
            time.sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', default='http://localhost:7079/api/v2')
    parser.add_argument('-prKey', required=True)
    parser.add_argument('-type', required=True)
    args = parser.parse_args()
    times = 120
    data = utils.login(args.url,
                            args.prKey, 0)
    token = data["jwtToken"] 
    if args.type == 'NewEcosystem':
        new_ecosystem(args.url, args.prKey, token, times)
    elif args.type == 'NewTable':
        new_table(args.url, args.prKey, token, times)
    elif args.type == 'NewPage':
        new_page(args.url, args.prKey, token, times)
    elif args.type == 'NewContract':
        new_contract(args.url, args.prKey, token, times)
    elif args.type == 'EditPage':
        edit_page(args.url, args.prKey, token, times)
    else:
        print("There is no contract with name " + args.type)