import requests
import time
import funcs
from builtins import sum

class CompareNodes(unittest.TestCase):
    
    def test_compare_nodes(self):
        fullConfig = config.getNodeConfig()
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        db1 = config1["dbName"]
        db2 = config2["dbName"]
        login1 = config1["login"]
        login2 = config2["login"]
        pas1 = config1["pass"]
        pas2 = config2["pass"]
        host1 = config1["dbHost"]
        host2 = config2["dbHost"]
        ts_count = 30
        self.data1 = utils.login(config1["url"], config1['private_key'])
        time.sleep(120)
        objects1 = utils.getCountDBObjects(host1, db1, login1, pas1)
        objects2 = utils.getCountDBObjects(host2, db2, login2, pas2)
        amounts1 = utils.getUserTokenAmounts(host1, db1, login1, pas1)
        amounts2 = utils.getUserTokenAmounts(host2, db2, login2, pas2)
        sumAmounts = sum(amount[0] for amount in amounts1)
        maxBlockId1 = funcs.get_max_block_id(config1["url"],self.data1["jwtToken"])
        self.data2 = utils.login(config2["url"], config1['private_key'])
        maxBlockId2 = funcs.get_max_block_id(config2["url"],self.data2["jwtToken"])
        maxBlock = max(maxBlockId2, maxBlockId1)
        hash1 = utils.get_blockchain_hash(host1, db1, login1, pas1, maxBlock)
        hash2 = utils.get_blockchain_hash(host2, db2, login2, pas2, maxBlock)
        node_position = utils.compare_node_positions(host1, db1, login1, pas1, maxBlock)
        dict1 = dict(count_contract = objects1["contracts"],
                     count_pages = objects1["pages"],
                     count_blocks = objects1["pages"],
                     count_tables = objects1["tables"],
                     count_menu = objects1["menus"],
                     count_params = objects1["params"],
                     count_locals = objects1["locals"],
                     amounts = amounts1, summ = sumAmounts,
                     hash = hash1,
                     node_pos = node_position)
        dict2 = dict(count_contract = objects2["contracts"],
                     count_pages = objects2["pages"],
                     count_blocks = objects2["pages"],
                     count_tables = objects2["tables"],
                     count_menu = objects2["menus"],
                     count_params = objects2["params"],
                     count_locals = objects2["locals"],
                     amounts = amounts2,
                     summ = 100000000000000000100000000,
                     hash = hash2,
                     node_pos = True)
        msg = "Test two_nodes is faild. contracts: \n"
        msg += str(objects1) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += str(objects2) + str(amounts1) + str(hash1) + str(node_position) + "\n"
        msg += "Amounts summ: " + str(sumAmounts)
        self.assertDictEqual(dict1, dict2, msg)

        
if __name__ == "__main__":
    unittest.main()