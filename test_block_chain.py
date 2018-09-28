import unittest
import time
from builtins import sum

from libs import actions, tools, db, check

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
    

        
    def test_db(self):
        tables = db.get_user_table_state(self.config1['db'], "1_contracts")
        print(tables)
    
