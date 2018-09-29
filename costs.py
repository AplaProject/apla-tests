import unittest
import utils
import config
import requests
import json
import funcs
import os
import time


class LimitsTestCase(unittest.TestCase):
    
    def setUp(self):
        global conf, contract
        conf = config.getNodeConfig()
        self.times = 120
        contract = config.readFixtures("contracts")
        global pause, token
        pause = conf["1"]["time_wait_tx_in_block"]
        self.data = utils.login(conf["2"]["url"],
                                conf["1"]['private_key'], 0)
        token = self.data["jwtToken"]        

    def test_new_ecosystem(self):
        i = 1
        while i < self.times:
            data = {"Name": "Ecosys_" + utils.generate_random_name()}
            utils.call_contract(config1["url"], config1['private_key'],
                                "NewEcosystem", data, token)
            i = i + 1
            time.sleep(5)
            
    def test_new_table(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"},{"name":"Myb","type":"json",
        "index": "0",  "conditions":"true"}, {"name":"MyD","type":"datetime",
        "index": "0",  "conditions":"true"}, {"name":"MyM","type":"money",
        "index": "0",  "conditions":"true"},{"name":"MyT","type":"text",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        i = 1
        while i < self.times:
            data = {"Name": "Tab_" + utils.generate_random_name(),
                    "Columns": column, "ApplicationId": 1, "Permissions": permission}
            utils.call_contract(config1["url"], config1['private_key'],
                                "NewTable", data, token)
            i = i + 1
            time.sleep(5)
            
    def test_new_page(self):
        i = 1
        while i < self.times:
            data = {"Name": "Page_" + utils.generate_random_name(),
                    "Value": "Hello page!", "ApplicationId": 1,
                    "Conditions": "true", "Menu": "default_menu"}
            utils.call_contract(config1["url"], config1['private_key'],
                                "NewPage", data, token)
            i = i + 1
            time.sleep(5)

    def test_new_contract(self):
        i = 1
        while i < self.times:
            code, name = utils.generate_name_and_code("")
            data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            utils.call_contract(config1["url"], config1['private_key'],
                                "NewContract", data, token)
            i = i + 1
            time.sleep(5)

    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        utils.call_contract(config1["url"], config1['private_key'],
                                "NewPage", data, token)
        status = utils.txstatus(config1["url"], 30, hash, token)
        if len(status['blockid']) > 0:
            i = 1
            while i < self.times:
                dataEdit = {"Id": funcs.get_count(url, "pages", token),
                    "Value": "Good by page!", "Conditions": "true",
                    "Menu": "default_menu"}
                utils.call_contract(config1["url"], config1['private_key'],
                                    "EditPage", dataEdit, token)
                i = i + 1
                time.sleep(5)


if __name__ == '__main__':
    unittest.main()