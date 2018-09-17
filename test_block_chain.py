import unittest
import time
from builtins import sum

from libs.actions import Actions
from libs.tools import Tools
from libs.db import Db

class TestBlockChain():

    def create_contract(self, url, prKey):
        code,name = Tools.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, "ApplicationId": 1,
                'Conditions': "ContractConditions(`MainCondition`)"}
        resp = Actions.call_contract(url, prKey, "NewContract", data, self.data1["jwtToken"])
        return name
    
    def edit_menu(self, url, prKey, id):
        dataEdit = {"Id": id, "Value": "tryam", "Conditions": "true"}
        res = Actions.call_contract(url, prKey, "EditMenu", dataEdit, self.data1["jwtToken"])
        
    def new_menu(self, url, prKey):
        name = "Menu_" + Tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = Actions.call_contract(url, prKey, "NewMenu", data, self.data1["jwtToken"])
        return Actions.get_count(url, "menu", self.data1["jwtToken"])
    
    def test_block_chain(self):
        fullConfig = Tools.read_config("nodes")
        nodes = len(fullConfig)
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        db1 = config1["db"]
        db2 = config2["db"]
        ts_count = 30
        self.data1 = Actions.login(config1["url"], config1['private_key'], 0)
        i = 1
        amountsB = Db.get_user_token_amounts(db1)
        sumAmountsBefore = sum(amount[0] for amount in amountsB)
        while i < ts_count:
            contName = self.create_contract(config1["url"],
                                            config1['private_key'],
                                            )
            i = i + 1
            time.sleep(1)
        time.sleep(120)

        count_contracts1 = Db.get_count_DB_objects(db1)["contracts"]
        count_contracts2 = Db.get_count_DB_objects(db2)["contracts"]
        amounts1 = Db.getUserTokenAmounts(db1)
        amounts2 = Db.getUserTokenAmounts(db2)
        sumAmounts = sum(amount[0] for amount in amounts1)
        maxBlockId1 = Actions.get_max_block_id(config1["url"], self.data1["jwtToken"])
        self.data2 = Actions.login(config2["url"], config1['private_key'], 0)
        maxBlockId2 = Actions.get_max_block_id(config2["url"], self.data2["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1)
        hash1 = Db.get_blockchain_hash(db1, maxBlock)
        hash2 = Db.get_blockchain_hash(db2, maxBlock)
        node_position = Db.compare_node_positions(db1, maxBlock, nodes)
        dict1 = dict(count_contract=count_contracts1,
                     amounts=str(amounts1), summ=str(sumAmounts),
                     hash=str(hash1),
                     node_pos=str(node_position))
        dict2 = dict(count_contract=count_contracts2,
                     amounts=str(amounts2),
                     summ=str(sumAmountsBefore),
                     hash=str(hash2),
                     node_pos="True")
        msg = "Test two_nodes is faild. contracts: \n"
        msg += str(count_contracts1) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += str(count_contracts2) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += "Amounts summ: " + str(sumAmounts)
        self.assertDictEqual(dict1, dict2, msg)
        
    def test_block_chain_edit(self):
        fullConfig = Tools.read_config("nodes")
        nodes = len(fullConfig)
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        db1 = config1["db"]
        db2 = config2["db"]
        ts_count = 100
        self.data1 = Actions.login(config1["url"], config1['private_key'], 0)
        id = self.new_menu(config1["url"], config1['private_key'])
        time.sleep(10)
        i = 1
        amountsB = Db.get_user_token_amounts(db1)
        sumAmountsBefore = sum(amount[0] for amount in amountsB)
        while i < ts_count:
            self.edit_menu(config1["url"],
                                      config1['private_key'], id)
            i = i + 1
        time.sleep(120)
        count_contracts1 = Db.getCountDBObjects(db1)["contracts"]
        count_contracts2 = Db.getCountDBObjects(db2)["contracts"]
        amounts1 = Db.get_user_token_amounts(db1)
        amounts2 = Db.get_user_token_amounts(db2)
        sumAmounts = sum(amount[0] for amount in amounts1)
        maxBlockId1 = Actions.get_max_block_id(config1["url"],self.data1["jwtToken"])
        self.data2 = Actions.login(config2["url"], config1['private_key'], 0)
        maxBlockId2 = Actions.get_max_block_id(config2["url"],self.data2["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1)
        hash1 = Db.get_blockchain_hash(db1, maxBlock)
        hash2 = Db.get_blockchain_hash(db2, maxBlock)
        node_position = Db.compare_node_positions(db1, maxBlock, nodes)
        dict1 = dict(count_contract = count_contracts1,
                     amounts = str(amounts1), summ = str(sumAmounts),
                     hash = str(hash1),
                     node_pos = str(node_position))
        dict2 = dict(count_contract = count_contracts2,
                     amounts = str(amounts2),
                     summ = str(sumAmountsBefore),
                     hash = str(hash2),
                     node_pos = "True")
        msg = "Test two_nodes is faild. contracts: \n"
        msg += str(count_contracts1) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += str(count_contracts2) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += "Amounts summ: " + str(sumAmounts)
        self.assertDictEqual(dict1, dict2, msg)
    
