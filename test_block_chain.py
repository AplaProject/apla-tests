import unittest
import time
from builtins import sum

from libs import actions
from libs import tools
from libs import db
from libs import check

class TestBlockChain():
    fullConfig = tools.read_config("nodes")
    nodes = len(fullConfig)
    config1 = fullConfig[0]
    config2 = fullConfig[1]
    db1 = config1["db"]
    db2 = config2["db"]

    def setup_class(self):
        self.uni = unittest.TestCase()
        data = actions.login(self.config1["url"], self.config1['private_key'], 0)
        self.token = data["jwtToken"]


    def create_contract(self, url, prKey):
        code, name = tools.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, "ApplicationId": 1,
                'Conditions': "ContractConditions(`MainCondition`)"}
        resp = actions.call_contract(url, prKey, "NewContract", data, self.token)
        return name
    
    def edit_menu(self, url, prKey, id):
        dataEdit = {"Id": id, "Value": "tryam", "Conditions": "true"}
        res = actions.call_contract(url, prKey, "EditMenu", dataEdit, self.token)
        
    def new_menu(self, url, prKey):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = actions.call_contract(url, prKey, "NewMenu", data, self.token)
        return actions.get_count(url, "menu", self.token)
    
    def test_block_chain(self):
        ts_count = 30
        i = 1
        amountsB = db.get_user_token_amounts(self.db1)
        sumAmountsBefore = sum(amount[0] for amount in amountsB)
        while i < ts_count:
            contName = self.create_contract(self.config1["url"],
                                            self.config1['private_key'])
            i = i + 1
            time.sleep(1)
        time.sleep(120)

        amountsAfter = db.get_user_token_amounts(self.db1)
        expect = {"isTheSameNodes": True, "isTheSameDB": True,
                      "sumAmounts": sumAmountsBefore}
        dict = {"isTheSameNodes": check.compare_nodes(self.fullConfig),
                "isTheSameDB": check.compare_db(self.fullConfig),
                      "sumAmounts": sum(amount[0] for amount in amountsAfter)}   
        self.uni.assertDictEqual(expect, dict, "Error in test_block_chain")
        
    def test_block_chain_edit(self):
        ts_count = 100
        id = self.new_menu(self.config1["url"], self.config1['private_key'])
        time.sleep(10)
        i = 1
        amountsB = db.get_user_token_amounts(self.db1)
        sumAmountsBefore = sum(amount[0] for amount in amountsB)
        while i < ts_count:
            self.edit_menu(self.config1["url"], self.config1['private_key'], id)
            i = i + 1
        time.sleep(120)
        
        amountsAfter = db.get_user_token_amounts(self.db1)
        expect = {"isTheSameNodes": True, "isTheSameDB": True,
                      "sumAmounts": sumAmountsBefore}
        dict = {"isTheSameNodes": check.compare_nodes(self.fullConfig),
                "isTheSameDB": check.compare_db(self.fullConfig),
                      "sumAmounts": sum(amount[0] for amount in amountsAfter)}   
        self.uni.assertDictEqual(expect, dict, "Error in test_block_chain_edit")
    
