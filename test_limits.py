import unittest
import json
import time

from libs import actions
from libs import tools
from libs import db


class TestLimits():

    def setup_class(self):
        global conf, contract, pause, token
        conf = tools.read_config("nodes")
        contract = tools.read_fixtures("contracts")
        pause = tools.read_config("test")["wait_tx_status"]
        self.data = actions.login(conf["2"]["url"],
                                  conf["1"]['private_key'], 0)
        token = self.data["jwtToken"]
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, result, jwtToken):
        self.unit.assertIn("hash", result)
        hash = result['hash']
        status = actions.tx_status(conf["2"]["url"], pause, hash, token)
        print("status tx: ", status)
        if int(status['blockid']) > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["error"]
        
    def call(self, name, data):
        resp = actions.call_contract(conf["2"]["url"], conf["1"]['private_key'],
                                     name, data, token)
        res = self.assert_tx_in_block(resp, token)
        return res
        
    def update_sys_param(self, param, value):
        data = {"Name": param, "Value" : value}
        res = self.call("UpdateSysParam", data)
        self.unit.assertGreater(int(res), 0,
                           "Block is not generated for updating sysparam: " +\
                           str(res))
        
    def test_max_tx_size(self):
        max_tx_size = db.get_system_parameter(conf["1"]["db"], "max_tx_size")
        self.update_sys_param("max_tx_size", "500")
        name = "cont" + tools.generate_random_name()
        code = "contract " + name + contract["limits"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.unit.assertEqual(error, "Max size of tx", "Incorrect error: " + error)
        self.update_sys_param("max_tx_size", str(max_tx_size))
        
    def test_max_block_size(self):
        max_block_size = db.get_system_parameter(conf["1"]["db"], "max_block_size")
        self.update_sys_param("max_block_size", "500")
        name = "cont" + tools.generate_random_name()
        code = "contract " + name + contract["limits"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.unit.assertEqual(error, "Max size of tx", "Incorrect error: " + error)
        self.update_sys_param("max_block_size", str(max_block_size))
        time.sleep(30)
      
    def test_max_block_user_tx(self):
        max_block_user_tx = db.get_system_parameter(conf["1"]["db"], "max_block_user_tx")
        self.update_sys_param("max_block_user_tx", "1")
        time.sleep(30)
        i = 1
        while i < 10: 
            name = "cont" + tools.generate_random_name()
            code = "contract " + name + contract["limits"]["code"]
            data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            actions.call_contract(conf["2"]["url"], conf["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = actions.get_max_block_id(conf["2"]["url"], token)
        print("maxBlock = ", maxBlock)
        isOneOrTwo = db.is_count_tx_in_block(conf["2"]["db"], maxBlock, 1)
        self.update_sys_param("max_block_user_tx ", str(max_block_user_tx ))
        time.sleep(30)
        self.unit.assertTrue(isOneOrTwo,
                        "One of block contains more than 2 transaction")
        
        
    def test_max_tx_count (self):
        max_tx_count = db.get_system_parameter(conf["1"]["db"], "max_tx_count")
        self.update_sys_param("max_tx_count", "2")
        i = 1
        while i < 10: 
            name = "cont" + tools.generate_random_name()
            code = "contract " + name + contract["limits"]["code"]
            data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            actions.call_contract(conf["2"]["url"], conf["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = actions.get_max_block_id(conf["2"]["url"], token)
        self.unit.assertTrue(db.is_count_tx_in_block(conf["2"]["db"], maxBlock, 2),
                        "One of block contains more than 2 transaction")
        self.update_sys_param("max_tx_count ", str(max_tx_count))
