import unittest
import pytest
from builtins import sum

from libs import actions
from libs import db
from libs import tools

class TestCompareNodes():
    config = tools.read_config("nodes")
    unit = unittest.TestCase()

    def test_compare_nodes(self):
        nodes = len(self.config)
        amounts1 = db.get_user_token_amounts(self.config["1"]["db"])
        amounts2 = db.get_user_token_amounts(self.config["2"]["db"])
        amounts3 = db.get_user_token_amounts(self.config["3"]["db"])    
        sumAmounts = sum(amount[0] for amount in amounts1)
        data1 = actions.login(self.config["1"]["url"], self.config["1"]['private_key'])
        maxBlockId1 = actions.get_max_block_id(self.config["1"]["url"], data1["jwtToken"])
        data2 = actions.login(self.config["2"]["url"], self.config["1"]['private_key'])
        maxBlockId2 = actions.get_max_block_id(self.config["2"]["url"], data2["jwtToken"])
        data3 = actions.login(self.config["3"]["url"], self.config["1"]['private_key'])
        maxBlockId3 = actions.get_max_block_id(self.config["3"]["url"], data3["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1, maxBlockId3)
        hash1 = db.get_blockchain_hash(self.config["1"]["db"], maxBlock)
        hash2 = db.get_blockchain_hash(self.config["2"]["db"], maxBlock)
        hash3 = db.get_blockchain_hash(self.config["3"]["db"], maxBlock)
        node_position = db.compare_node_positions(self.config["1"]["db"], maxBlock, nodes)
        dict1 = dict(amounts=str(amounts1),
                     hash=str(hash1),
                     node_pos=str(node_position))
        dict2 = dict(amounts=str(amounts2),
                     hash=str(hash2),
                     node_pos="True")
        dict3 = dict(amounts=str(amounts3),
                     hash=str(hash3),
                     node_pos="True")
        msg = "Test three nodes is faild. contracts: \n"
        msg += str(amounts1) + str(hash1) + "\n"
        msg += str(amounts2) + str(hash2) + "\n"
        msg += str(amounts3) + str(hash3) + str(node_position) + "\n"
        msg += "Amounts summ: " + str(sumAmounts)
        self.unit.assertDictEqual(dict1, dict2, msg)
        self.unit.assertDictEqual(dict1, dict3, msg)

    def test_compare_db(self):
        dbInformation1 = db.get_count_DB_objects(self.config["1"]["db"])
        dbInformation2 = db.get_count_DB_objects(self.config["2"]["db"])
        dbInformation3 = db.get_count_DB_objects(self.config["3"]["db"])
        for key in dbInformation1:
            dbInf1 = dbInformation1[key]
            dbInf2 = dbInformation2[key]
            dbInf3 = dbInformation3[key]
        self.unit.assertEqual(dbInf1, dbInf2, "Different info about " + key)
        self.unit.assertEqual(dbInf1, dbInf3, "Different info about " + key)


if __name__ == '__main__':
    unittest.main()