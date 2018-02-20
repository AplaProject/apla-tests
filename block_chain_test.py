import unittest
import utils
import config
import requests
import time
import funcs
from builtins import sum

class BlockChainTestCase(unittest.TestCase):

    def create_contract(self, url, prKey):
        code,name = utils.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, 'Conditions': "ContractConditions(`MainCondition`)"}
        resp = utils.call_contract(url, prKey, "NewContract", data, self.data1["jwtToken"])
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
        self.data1 = utils.login(config1["url"], config1['private_key'])
        i = 1
        while i < ts_count:
            contName = self.create_contract(config1["url"], config1['private_key'])
            i = i + 1
            time.sleep(1)
        time.sleep(15)
        count_contracts1 = utils.getCountDBObjects(host1, db1, login1, pas1)["contracts"]
        count_contracts2 = utils.getCountDBObjects(host2, db2, login2, pas2)["contracts"]
        fail = 0
        msg = ""
        if(count_contracts1 != count_contracts2):
            fail = fail + 1
            msg = msg + "Different count of contracts"
        amounts1 = utils.getAmounts(host1, db1, login1, pas1)
        amounts2 = utils.getAmounts(host2, db2, login2, pas2)
        if(amounts1 != amounts2):
            fail = fail + 1
            msg = msg + " Different values of amounts"
        summ = 0
        i = 0
        while i < len(amounts1):
            summ = summ + int(amounts1[i][0])
            i = i + 1
        if(summ != 100000000000000000100000000):
            fail = fail + 1
            msg = msg + " Summ of amounts is not 100000000000000000100000000 Summ"
        maxBlockId1 = funcs.get_max_block_id(config1["url"],self.data1["jwtToken"])
        self.data2 = utils.login(config2["url"], config1['private_key'])
        maxBlockId2 = funcs.get_max_block_id(config2["url"],self.data1["jwtToken"])
        if(maxBlockId1 > maxBlockId2):
            maxBlock = maxBlockId2
        else:
            maxBlock = maxBlockId1
        hash1 = utils.get_blockchain_hash(host1, db1, login1, pas1, maxBlock)
        hash2 = utils.get_blockchain_hash(host2, db2, login2, pas2, maxBlock)
        if(hash1 != hash2):
            fail = fail + 1
            msg = msg + " Hashes of block_chain are differents"
        node_position = utils.compare_node_positions(host1, db1, login1, pas1, maxBlock)
        if(node_position != True):
            fail = fail + 1
            msg = msg + " Node_positions did not order correctly" 
        self.assertLess(fail, 1, msg)

        
if __name__ == "__main__":
    unittest.main()
    
