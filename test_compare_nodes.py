import unittest
import utils
import config
import requests
import time
import funcs
from builtins import sum

class TestCompareNodes(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global config1, config2, config3, db1, db2, db3, login1, login2, login3
        global pas1, pas2, pas3, host1, host2, host3
        fullConfig = config.getNodeConfig()
        nodes = len(fullConfig)
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        config3 = fullConfig["3"]
        db1 = config1["dbName"]
        db2 = config2["dbName"]
        db3 = config3["dbName"]
        login1 = config1["login"]
        login2 = config2["login"]
        login3 = config3["login"]
        pas1 = config1["pass"]
        pas2 = config2["pass"]
        pas3 = config3["pass"]
        host1 = config1["dbHost"]
        host2 = config2["dbHost"]
        host3 = config3["dbHost"]
    
    def test_compare_nodes(self):
        nodes = 3
        amounts1 = utils.getUserTokenAmounts(host1, db1, login1, pas1)
        amounts2 = utils.getUserTokenAmounts(host2, db2, login2, pas2)
        amounts3 = utils.getUserTokenAmounts(host3, db3, login3, pas3)
        sumAmounts = sum(amount[0] for amount in amounts1)
        self.data1 = utils.login(config1["url"], config1['private_key'], 0)
        maxBlockId1 = funcs.get_max_block_id(config1["url"],self.data1["jwtToken"])
        self.data2 = utils.login(config2["url"], config1['private_key'], 0)
        maxBlockId2 = funcs.get_max_block_id(config2["url"],self.data2["jwtToken"])
        self.data3 = utils.login(config3["url"], config1['private_key'], 0)
        maxBlockId3 = funcs.get_max_block_id(config3["url"],self.data3["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1, maxBlockId3)
        hash1 = utils.get_blockchain_hash(host1, db1, login1, pas1, maxBlock)
        hash2 = utils.get_blockchain_hash(host2, db2, login2, pas2, maxBlock)
        hash3 = utils.get_blockchain_hash(host3, db3, login3, pas3, maxBlock)
        node_position = utils.compare_node_positions(host1, db1, login1, pas1, maxBlock, nodes)
        dict1 = dict(amounts = str(amounts1),
                     hash = str(hash1),
                     node_pos = str(node_position))
        dict2 = dict(amounts = str(amounts2),
                     hash = str(hash2),
                     node_pos = "True")
        dict3 = dict(amounts = str(amounts3),
                     hash = str(hash3),
                     node_pos = "True")
        msg = "Test three nodes is faild. contracts: \n"
        msg += str(amounts1) + str(hash1) + "\n"
        msg += str(amounts2) + str(hash2) + "\n"
        msg += str(amounts3) + str(hash3) + str(node_position) + "\n"
        msg += "Amounts summ: " + str(sumAmounts)
        self.assertDictEqual(dict1, dict2, msg)
        self.assertDictEqual(dict1, dict3, msg)
        
    def test_compare_db(self):
        dbInformation1 = utils.getCountDBObjects(host1, db1, login1, pas1)
        dbInformation2 = utils.getCountDBObjects(host2, db2, login2, pas2)
        dbInformation3 = utils.getCountDBObjects(host3, db3, login3, pas3)
        for key in dbInformation1:
            dbInf1 = dbInformation1[key]
            dbInf2 = dbInformation2[key]
            dbInf3 = dbInformation3[key]
        self.assertEqual(dbInf1, dbInf2,"Different info about " + key)
        self.assertEqual(dbInf1, dbInf3,"Different info about " + key)
