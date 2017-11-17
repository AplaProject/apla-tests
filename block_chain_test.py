import unittest
import utils
import hostconfig
import requests

class BlockChainTestCase(unittest.TestCase):
    url = hostconfig.getConfig()['url1'] 
    privateKey = hostconfig.getConfig()['private_key1']
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

    def test_block_chain(self):
        contName = self.create_contract()
        utils.get_block_chain()
        

    def change_contract(self):
        item = self.get_first_contract_item()
        _, code = self.get_name_and_code()
        data = {'value': code, "conditions": """ContractConditions(`MainCondition`)"""}
        sign_res = utils.prepare_tx('PUT', 'contract', item['id'], self.data['cookie'], data)
        data.update(sign_res)
        resp = requests.put(self.url+'/contract/'+item['id'], data=data, headers={"Cookie": self.data['cookie']})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertTxInBlock(result)
        
if __name__ == "__main__":
    unittest.main()
    
