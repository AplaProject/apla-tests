import unittest
import time
from builtins import sum

from libs import actions, tools, check, db

class TestBlockChain():
    full_config = tools.read_config("nodes")
    nodes = len(full_config)
    config1 = full_config[0]
    config2 = full_config[1]

    def setup_class(self):
        self.uni = unittest.TestCase()
        data = actions.login(self.config1["url"], self.config1['private_key'], 0)
        self.token = data["jwtToken"]


    def create_contract(self, url, pr_key):
        code, name = tools.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, "ApplicationId": 1,
                'Conditions': "ContractConditions(\"MainCondition\")"}
        resp = actions.call_contract(url, pr_key, "NewContract", data, self.token)
        return name
    
    def edit_menu(self, url, pr_key, id):
        data_edit = {"Id": id, "Value": "tryam", "Conditions": "true"}
        res = actions.call_contract(url, pr_key, "EditMenu", data_edit, self.token)
        
    def new_menu(self, url, pr_key):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = actions.call_contract(url, pr_key, "NewMenu", data, self.token)
        return actions.get_count(url, "menu", self.token)
    
    def test_ee(self):
        res = db.get_table_hash(self.config1['db'], "1_pages")
        print(res)
        ans = db.get_table_hash(db22, "1_pages")
    
    def test_block_chain(self):
        ts_count = 30
        i = 1
        amounts_b = actions.get_user_token_amounts(self.config1["url"], self.token)
        print('amounts_b', amounts_b)
        sum_amounts_before = sum(amounts_b)
        while i < ts_count:
            contName = self.create_contract(self.config1["url"],
                                            self.config1['private_key'])
            i = i + 1
            time.sleep(1)
        time.sleep(120)

        amounts_after = actions.get_user_token_amounts(self.config1["url"], self.token)
        expect = {"isTheSameNodes": True, "isTheSameDB": True,
                      "sumAmounts": sum_amounts_before}
        dict = {"isTheSameNodes": check.compare_nodes(self.full_config),
                "isTheSameDB": check.compare_db(self.full_config, self.config1["url"], self.token),
                      "sumAmounts": sum(amounts_after)}   
        self.uni.assertDictEqual(expect, dict, "Error in test_block_chain")
        
    def test_block_chain_edit(self):
        ts_count = 100
        id = self.new_menu(self.config1["url"], self.config1['private_key'])
        time.sleep(10)
        i = 1
        amounts_b = actions.get_user_token_amounts(self.config1["url"], self.token)
        sum_amounts_before = sum(amounts_b)
        while i < ts_count:
            self.edit_menu(self.config1["url"], self.config1['private_key'], id)
            i = i + 1
        time.sleep(120)
        
        amounts_after = actions.get_user_token_amounts(self.config1["url"], self.token)
        expect = {"isTheSameNodes": True, "isTheSameDB": True,
                      "sumAmounts": sum_amounts_before}
        dict = {"isTheSameNodes": check.compare_nodes(self.full_config),
                "isTheSameDB": check.compare_db(self.full_config, self.config1["url"], self.token),
                      "sumAmounts": sum(amounts_after)}   
        self.uni.assertDictEqual(expect, dict, "Error in test_block_chain_edit")
    
