import unittest
import utils
import config
import requests
from objects import Contracts

class ContractFunctionsTestCase(unittest.TestCase):  
    def setUp(self):
        config.readMainConfig()
        self.data = utils.login()  

    def assertTxInBlock(self, result, jvtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(result['hash'], jvtToken)
        self.assertEqual(status['errmsg'], "")
        self.assertGreater(len(status['blockid']), 0)
        
    def generate_name_and_code(self, sourseCode):
        name = utils.generate_random_name()
        code = "contract " + name + sourseCode
        return code, name

    def create_contract(self, code):
        data = {'Wallet': '', 'Value': code, 'Conditions': """ContractConditions(`MainCondition`)"""}
        result = utils.call_contract("NewContract", data, self.data["jvtToken"])
        self.assertTxInBlock(result, self.data["jvtToken"])
    
    def check_contract(self, sourse, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        hash = utils.call_contract(name, {}, self.data["jvtToken"])["hash"]
        result = utils.txstatus(hash, self.data["jvtToken"])
        self.assertIn(checkPoint, result["result"], "error")
    
    def test_contract_dbfind(self):
        self.check_contract(*Contracts.dbFind)
        
    def test_contract_dbAmount(self):
        self.check_contract(*Contracts.dbAmount)
        
    def test_contract_ecosysParam(self):
        self.check_contract(*Contracts.ecosysParam)
        
    def test_contract_dbIntExt(self):
        self.check_contract(*Contracts.dbIntExt)
        
    def test_contract_dbIntWhere(self):
        self.check_contract(*Contracts.dbIntWhere)
        
    def test_contract_DBIntWhere(self):
        self.check_contract(*Contracts.DBIntWhere)

if __name__ == '__main__':
    unittest.main()