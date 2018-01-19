import unittest
import utils
import config
import requests
import time

class BlockChainTestCase(unittest.TestCase):

    def assertTxInBlock(self, result, jvtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(result['hash'], jvtToken)
        self.assertEqual(status['errmsg'], "")
        self.assertGreater(len(status['blockid']), 0)
        
    def get_name_and_code(self):
        name = utils.generate_random_name()
        code = """contract %s {
                       conditions {}
                       action {}
                    }""" % (name,)
        return code,name
    
    def generate_code(self, name):
        code = """contract %s {
                       conditions {}
                       action {
                       var test string}
                    }""" % (name,)
        return code

    def create_contract(self):
        code,name = self.get_name_and_code()
        data = {'Wallet': '', 'Value': code, 'Conditions': """ContractConditions(`MainCondition`)"""}
        resp = utils.call_contract("NewContract", data, self.data["jvtToken"])
        return name


    def get_count_contract(self):
        resp = requests.get(config.config["url"] + '/list/contracts', headers={"Authorization": self.data["jvtToken"]})
        result = resp.json()
        return result["count"]
    
    def change_contract(self, id, code):
        data = {'Value': code, "Conditions": """ContractConditions(`MainCondition`)""", "Id": id}
        sign_res = utils.prepare_tx('EditContract', self.data['jvtToken'], data)
        data.update(sign_res)
        resp = requests.post(config.config["url"] + '/contract/EditContract', data=data, headers={"Authorization": self.data["jvtToken"]})
        result = resp.json()
        self.assertTxInBlock(result, self.data["jvtToken"])
    
    def test_block_chain(self):
        db1 = "aplafront"
        db2 = "apla2"
        login = "postgres"
        pas = "postgres"
        host ="localhost"
        ts_count = 30
        config.readMainConfig()
        print(config.config["private_key"])
        self.data = utils.login()
        i = 1
        while i < ts_count:
            contName = self.create_contract()
            i = i + 1
        time.sleep(5)
        self.assertTrue(utils.get_count_records_block_chain(host, db1, login, pas), "There isn't 30 records in block_chain1")
        self.assertTrue(utils.get_count_records_block_chain(host, db2, login, pas), "There isn't 30 records in block_chain2")
        count_contracts1 = utils.getCountDBObjects(host, db1, login, pas)["contracts"]
        count_contracts2 = utils.getCountDBObjects(host, db2, login, pas)["contracts"]
        self.assertTrue(utils.compare_keys_cout(host, db2, login, pas), "There are different count of keys in block_chain")
        self.assertTrue(utils.compare_node_positions(host, db1, login, pas), "Incorrect order of nodes in block_chain")
        self.assertEqual(count_contracts1, count_contracts2,"Different count")
        
if __name__ == "__main__":
    unittest.main()
    
