import unittest
import config
from builtins import sum

from libs.actions import Actions
from libs.tools import Tools

class CompareNodes(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global config1, config2, config3, db1, db2, db3
        fullConfig = Tools.readConfig("nodes")
        nodes = len(fullConfig)
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        config3 = fullConfig["3"]
        db1 = config1["db"]
        db2 = config2["db"]
        db3 = config3["db"]
    
    def test_compare_nodes(self):
        nodes = 3
        amounts1 = Actions.get_user_token_amounts(db1)
        amounts2 = Actions.get_user_token_amounts(db2)
        amounts3 = Actions.get_user_token_amounts(db3)
        sumAmounts = sum(amount[0] for amount in amounts1)
        self.data1 = Actions.login(config1["url"], config1['private_key'], 0)
        maxBlockId1 = Actions.get_max_block_id(config1["url"],self.data1["jwtToken"])
        self.data2 = Actions.login(config2["url"], config1['private_key'], 0)
        maxBlockId2 = Actions.get_max_block_id(config2["url"],self.data2["jwtToken"])
        self.data3 = Actions.login(config3["url"], config1['private_key'], 0)
        maxBlockId3 = Actions.get_max_block_id(config3["url"],self.data3["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1, maxBlockId3)
        hash1 = Db.get_blockchain_hash(db1, maxBlock)
        hash2 = Db.get_blockchain_hash(db2, maxBlock)
        hash3 = Db.get_blockchain_hash(db3, maxBlock)
        node_position = Db.compare_node_positions(db1, maxBlock, nodes)
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
        dbInformation1 = Actions.get_count_DB_objects(db1)
        dbInformation2 = Actions.get_count_DB_objects(db2)
        dbInformation3 = Actions.get_count_DB_objects(db3)
        for key in dbInformation1:
            dbInf1 = dbInformation1[key]
            dbInf2 = dbInformation2[key]
            dbInf3 = dbInformation3[key]
        self.assertEqual(dbInf1, dbInf2,"Different info about " + key)
        self.assertEqual(dbInf1, dbInf3,"Different info about " + key)


if __name__ == '__main__':
    unittest.main()