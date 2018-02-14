import unittest
import utils
import config
import requests
import json


class ContractFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.readMainConfig()
        self.contracts = config.readFixtures("contracts")
        self.data = utils.login(self.config["url"], self.config['private_key'])

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash",  result)
        sleep = self.config["time_wait_tx_in_block"]
        url = self.config["url"]
        status = utils.txstatus(url, sleep, result['hash'], jwtToken)
        self.assertNotIn(json.dumps(status), 'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def generate_name_and_code(self, sourseCode):
        name = utils.generate_random_name()
        code = "contract " + name + sourseCode
        return code, name

    def create_contract(self, code):
        data = {}
        data["Wallet"] = ""
        data["Value"] = code
        data["Conditions"] = "ContractConditions(`MainCondition`)"
        url = self.config["url"]
        prKey = self.config['private_key']
        token = self.data["jwtToken"]
        result = utils.call_contract(url, prKey, "NewContract", data, token)
        self.assertTxInBlock(result, self.data["jwtToken"])

    def check_contract(self, sourse, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        url = self.config["url"]
        prKey = self.config['private_key']
        token = self.data["jwtToken"]
        sleep = self.config["time_wait_tx_in_block"]
        res = utils.call_contract(url, prKey, name, {}, token)
        hash = res["hash"]
        result = utils.txstatus(url, sleep, hash, token)
        self.assertIn(checkPoint, result["result"], "error")

    def test_contract_dbfind(self):
        contract = self.contracts["dbFind"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ecosysParam(self):
        contract = self.contracts["ecosysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_dbRow(self):
        contract = self.contracts["dbRow"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ifMap(self):
        contract = self.contracts["ifMap"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_evalCondition(self):
        contract = self.contracts["evalCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_validateCondition(self):
        contract = self.contracts["validateCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_addressToId(self):
        contract = self.contracts["addressToId"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_contains(self):
        contract = self.contracts["contains"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_float(self):
        contract = self.contracts["float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hasPrefix(self):
        contract = self.contracts["hasPrefix"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hexToBytes(self):
        contract = self.contracts["hexToBytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_Int(self):
        contract = self.contracts["int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_len(self):
        contract = self.contracts["len"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_pubToID(self):
        contract = self.contracts["pubToID"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_replace(self):
        contract = self.contracts["replace"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_size(self):
        contract = self.contracts["size"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sha256(self):
        contract = self.contracts["sha256"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_Sprintf(self):
        contract = self.contracts["sprintf"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_str(self):
        contract = self.contracts["str"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_substr(self):
        contract = self.contracts["substr"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_updateLang(self):
        contract = self.contracts["updateLang"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamString(self):
        contract = self.contracts["sysParamString"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamInt(self):
        contract = self.contracts["updSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_updSysParam(self):
        contract = self.contracts["updSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_updateSysParam(self):
        contract = self.contracts["updateSysParam"]
        self.check_contract(contract["code"], contract["asert"])

    # branch 421-contractnames
    def test_contract_getContractById(self):
        contract = self.contracts["getContractById"]
        self.check_contract(contract["code"], contract["asert"])

    # branch 421-contractnames
    def test_contract_getContractByName(self):
        contract = self.contracts["getContractByName"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_random(self):
        contract = self.contracts["random"]
        self.check_contract(contract["code"], contract["asert"])

if __name__ == '__main__':
    unittest.main()
