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
        
    def test_contract_ecosysParam(self):
        self.check_contract(*Contracts.ecosysParam)
    
    def test_contract_dbRow(self):
        self.check_contract(*Contracts.dbRow)
        
    def test_contract_ifMap(self):
        self.check_contract(*Contracts.ifMap)    
        
    def test_contract_evalCondition(self):
        self.check_contract(*Contracts.evalCondition)
        
    def test_contract_validateCondition(self):
        self.check_contract(*Contracts.validateCondition)
        
    def test_contract_addressToId(self):
        self.check_contract(*Contracts.addressToId)
        
    def test_contract_contains(self):
        self.check_contract(*Contracts.contains)
        
    def test_contract_float(self):
        self.check_contract(*Contracts.float)
        
    def test_contract_hasPrefix(self):
        self.check_contract(*Contracts.hasPrefix)
        
    def test_contract_hexToBytes(self):
        self.check_contract(*Contracts.hexToBytes)
        
    def test_contract_Int(self):
        self.check_contract(*Contracts.Int)
        
    def test_contract_len(self):
        self.check_contract(*Contracts.len)
        
    def test_contract_pubToID(self):
        self.check_contract(*Contracts.pubToID)
        
    def test_contract_replace(self):
        self.check_contract(*Contracts.replace)
        
    def test_contract_size(self):
        self.check_contract(*Contracts.size)
        
    def test_contract_sha256(self):
        self.check_contract(*Contracts.sha256)
        
    def test_contract_Sprintf(self):
        self.check_contract(*Contracts.Sprintf)
        
    def test_contract_str(self):
        self.check_contract(*Contracts.str)
        
    def test_contract_substr(self):
        self.check_contract(*Contracts.substr)
        
    def test_contract_updateLang(self):
        self.check_contract(*Contracts.updateLang)
        
    def test_contract_sysParamString(self):
        self.check_contract(*Contracts.sysParamString)
        
    def test_contract_sysParamInt(self):
        self.check_contract(*Contracts.sysParamInt)
        
    def test_contract_updSysParam(self):
        self.check_contract(*Contracts.updSysParam)

if __name__ == '__main__':
    unittest.main()