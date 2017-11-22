import unittest
import utils
import config
import requests

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
        sign_res = utils.prepare_tx('NewContract', self.data['jvtToken'], data)
        data.update(sign_res)
        resp = requests.post(config.config["url"] + '/contract/NewContract', data=data, headers={"Authorization": self.data["jvtToken"]})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertTxInBlock(result, self.data["jvtToken"])
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
        config.getNodeConfig("1")
        self.data = utils.login()
        i = 1
        while i < 10:
            contName = self.create_contract()
            code = self.generate_code(contName)
            countContracts = self.get_count_contract()
            self.change_contract(countContracts, code)
            i = i + 1
        config.getNodeConfig("2")
        self.data = utils.login()
        i = 1
        while i < 10:
            contName = self.create_contract()
            code = self.generate_code(contName)
            countContracts = self.get_count_contract()
            self.change_contract(countContracts, code)
            i = i + 1 
        self.assertTrue(utils.compare_keys_cout(), "There are different count of keys in block_chain")
        
if __name__ == "__main__":
    unittest.main()
    
