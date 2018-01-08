import unittest
import utils
import config
import requests


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        config.readMainConfig()
        self.data = utils.login() 
        
    def assertTxInBlock(self, result, jvtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(result['hash'], jvtToken)
        self.assertNotIn(json.dumps(status),'errmsg')
        self.assertGreater(len(status['blockid']), 0)
        
    def generate_name_and_code(self, sourseCode):
        name = utils.generate_random_name()
        code = "contract " + name + sourseCode
        return code, name
    
    def call_get_api(self, endPoint, data, asserts):
        resp = requests.get(config.config['url']+ endPoint, data=data,  headers={"Authorization": self.data["jvtToken"]})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        for asert in asserts:
            self.assertIn(asert, result)
       
    def test_balance(self):
        asserts = ["amount", "money"]
        self.call_get_api('/balance/' + self.data['address'], "", asserts)
        
    def test_getEcosystem(self):
        asserts = ["number"]
        self.call_get_api("/ecosystems/", "", asserts)
        
    def test_get_param_ecosystem(self):
        asserts = ["list"]
        data = {'ecosystem': 1} 
        self.call_get_api("/ecosystemparams/", data, asserts)
        
    def test_get_param_current_ecosystem(self):
        asserts = ["list"]
        self.call_get_api("/ecosystemparams/", "", asserts)
        
    def test_get_params_ecosystem_with_names(self):
        asserts = ["list"]
        data = {'ecosystem': 1, 'names':"name"} 
        self.call_get_api("/ecosystemparams/", data, asserts)
        
    def test_get_parametr_of_current_ecosystem(self):
        asserts = ["id", "name", "value", "conditions"]
        data = {}
        self.call_get_api("/ecosystemparam/founder_account/", data, asserts)
        
    def test_get_tables_of_current_ecosystem(self):
        asserts = ["list", "count"]
        data = {}
        self.call_get_api("/tables", data, asserts)
        
    def test_get_table_information(self):
        asserts = ["name"]
        data = {}
        self.call_get_api("/table/contracts", data, asserts)
        
if __name__ == '__main__':
    unittest.main()
    #utils.install("PRIVATE_NET", "ERROR", "localhost", "5432", "aplafront", "postgres", "postgres", "1", "")      
        