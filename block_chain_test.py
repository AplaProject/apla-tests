import unittest
import utils
import config
import requests
import time

class BlockChainTestCase(unittest.TestCase):

    def create_contract(self, url, prKey):
        code,name = utils.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, 'Conditions': """ContractConditions(`MainCondition`)"""}
        resp = utils.call_contract(url, prKey, "NewContract", data, self.data["jvtToken"])
        return name
    
    def test_block_chain(self):
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
        self.data = utils.login(config1["url"], config1['private_key'])
        i = 1
        while i < ts_count:
            contName = self.create_contract(config1["url"], config1['private_key'])
            i = i + 1
            time.sleep(1)
        time.sleep(15)
        self.assertEqual(utils.get_count_records_block_chain(host1, db1, login1, pas1), 30, "There isn't 30 records in block_chain1")
        self.assertEqual(utils.get_count_records_block_chain(host2, db2, login2, pas2), 30, "There isn't 30 records in block_chain2")
        count_contracts1 = utils.getCountDBObjects(host1, db1, login1, pas1)["contracts"]
        count_contracts2 = utils.getCountDBObjects(host2, db2, login2, pas2)["contracts"]
        self.assertTrue(utils.compare_node_positions(host1, db1, login1, pas1), "Incorrect order of nodes in block_chain")
        self.assertEqual(count_contracts1, count_contracts2,"Different count")
        self.assertTrue(utils.compare_keys_cout(host1, db2, login1, pas1), "There are different count of keys in block_chain")
        
if __name__ == "__main__":
    unittest.main()
    
