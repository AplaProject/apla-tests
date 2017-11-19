import unittest
import utils
import hostconfig
import requests

class BlockChainTestCase(unittest.TestCase):
    url = ""
    privateKey = ""
    wait = hostconfig.getConfig()['time_wait_tx_in_block']
    
    def setUp(self):
        self.data = utils.login(self.url, self.privateKey)

    def assertTxInBlock(self, result, jvtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(result['hash'], self.url, jvtToken,self.wait)
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
        sign_res = utils.prepare_tx('POST', 'NewContract', "", self.data['jvtToken'], data, self.url, self.privateKey)
        data.update(sign_res)
        resp = requests.post(self.url + '/contract/NewContract', data=data, headers={"Authorization": self.data["jvtToken"]})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertTxInBlock(result, self.data["jvtToken"])
        return name


    def get_count_contract(self):
        resp = requests.get(self.url + '/list/contracts', headers={"Authorization": self.data["jvtToken"]})
        result = resp.json()
        return result["count"]
    
    def change_contract(self, id, code):
        data = {'Value': code, "Conditions": """ContractConditions(`MainCondition`)""", "Id": id}
        sign_res = utils.prepare_tx('POST', 'EditContract', "", self.data['jvtToken'], data, self.url, self.privateKey)
        data.update(sign_res)
        resp = requests.post(self.url+'/contract/EditContract', data=data, headers={"Authorization": self.data["jvtToken"]})
        result = resp.json()
        self.assertTxInBlock(result, self.data["jvtToken"])
    
    def test_block_chain(self):
        url = hostconfig.getConfig()['url1'] 
        privateKey = hostconfig.getConfig()['private_key1']
        i = 1
        while i < 10:
            contName = self.create_contract()
            code = self.generate_code(contName)
            countContracts = self.get_count_contract()
            self.change_contract(countContracts, code)
            i = i + 1
        url = hostconfig.getConfig()['url2']
        privateKey = hostconfig.getConfig()['private_key2']
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
    
