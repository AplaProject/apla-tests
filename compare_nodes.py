import unittest
import pytest
from builtins import sum

from libs import actions
from libs import db
from libs import tools

class TestCompareNodes():
    config = tools.read_config("nodes")
    unit = unittest.TestCase()
    nodes = len(config)

    def test_compare_nodes(self):
        amounts = []
        data = []
        maxBlockId = []
        i = 0 
        while i < self.nodes:
            amounts.append(db.get_user_token_amounts(self.config[i]["db"]))
            data.append(actions.login(self.config[i]["url"], self.config[0]['private_key']))
            maxBlockId.append(actions.get_max_block_id(self.config[i]["url"], data[i]["jwtToken"]))
            i += 1   

        maxBlock = max(maxBlockId)
        hash = []
        i = 0 
        while i < self.nodes:
            hash.append(db.get_blockchain_hash(self.config[i]["db"], maxBlock))
            i += 1 
        node_position = db.compare_node_positions(self.config[0]["db"], maxBlock, self.nodes)
        
        mainDict = {"amounts": str(amounts[0]),
                     "hash": str(hash[0]),
                     "node_pos": "True"}
        dict = []
        i = 0 
        while i < self.nodes:
            dict.append({"amounts": str(amounts[i]),
                             "hash": str(hash[i]),
                             "node_pos": str(node_position)})
            self.unit.assertDictEqual(mainDict, dict[i], "Error in block_chain")
            i += 1
        

    def test_compare_db(self):
        dbInformation = []
        i = 0 
        while i < self.nodes:
            dbInformation.append(db.get_count_DB_objects(self.config[i]["db"]))
            dbInf = []
            for key in dbInformation[i]:
                print("i", i)
                dbInf.append(dbInformation[i][key])
            if(i > 0):
                self.unit.assertEqual(dbInf[i-1], dbInf[i], "Different info about " + key)
            i += 1


if __name__ == '__main__':
    unittest.main()