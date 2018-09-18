import unittest
import json
import time

from libs.actions import Actions
from libs.tools import Tools
from libs.db import Db


class TestLimits(unittest.TestCase):

    @classmethod

    def setup_class(self):
        global conf, contract, pause, token
        conf = Tools.read_config("nodes")
        contract = Tools.read_fixtures("contracts")
        pause = Tools.read_config("test")["wait_tx_status"]
        self.data = Actions.login(conf["2"]["url"],
                                  conf["1"]['private_key'], 0)
        token = self.data["jwtToken"]

    def assert_tx_in_block(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = Actions.tx_status(conf["2"]["url"], pause, hash, token)
        print("status tx: ", status)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]
        
    def call(self, name, data):
        resp = Actions.call_contract(conf["2"]["url"], conf["1"]['private_key'],
                                     name, data, token)
        res = self.assert_tx_in_block(resp, token)
        return res
        
    def update_sys_param(self, param, value):
        data = {"Name": param, "Value" : value}
        res = self.call("UpdateSysParam", data)
        self.assertGreater(int(res), 0,
                           "Block is not generated for updating sysparam: " +\
                           res)
        
    def test_max_tx_size(self):
        max_tx_size = Db.get_system_parameter(conf["1"]["db"], "max_tx_size")
        self.update_sys_param("max_tx_size", "500")
        name = "cont" + Tools.generate_random_name()
        code = "contract " + name + contract["limits"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.assertEqual(error, "Max size of tx", "Incorrect error: " + error)
        self.update_sys_param("max_tx_size", str(max_tx_size))
        
    def test_max_block_size(self):
        max_block_size = Db.get_system_parameter(conf["1"]["db"], "max_block_size")
        self.update_sys_param("max_block_size", "500")
        name = "cont" + Tools.generate_random_name()
        code = "contract " + name + contract["limits"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.assertEqual(error, "stop generating block", "Incorrect error: " + error)
        self.update_sys_param("max_block_size", str(max_block_size))
        time.sleep(30)
      
    def test_max_block_user_tx(self):
        max_block_user_tx = Db.get_system_parameter(conf["1"]["db"], "max_block_user_tx")
        self.update_sys_param("max_block_user_tx", "1")
        time.sleep(30)
        i = 1
        while i < 10: 
            name = "cont" + Tools.generate_random_name()
            code = "contract " + name + contract["limits"]["code"]
            data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            Actions.call_contract(conf["2"]["url"], conf["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = Actions.get_max_block_id(conf["2"]["url"], token)
        print("maxBlock = ", maxBlock)
        isOneOrTwo = Db.is_count_tx_in_block(conf["2"]["db"], maxBlock, 1)
        self.update_sys_param("max_block_user_tx ", str(max_block_user_tx ))
        time.sleep(30)
        self.assertTrue(isOneOrTwo,
                        "One of block contains more than 2 transaction")
        
        
    def test_max_tx_count (self):
        max_tx_count = Db.get_system_parameter(conf["1"]["db"], "max_tx_count")
        self.update_sys_param("max_tx_count", "2")
        i = 1
        while i < 10: 
            name = "cont" + Tools.generate_random_name()
            code = "contract " + name + contract["limits"]["code"]
            data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            Actions.call_contract(conf["2"]["url"], conf["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = Actions.get_max_block_id(conf["2"]["url"], token)
        self.assertTrue(Db.is_count_tx_in_block(conf["2"]["db"], maxBlock, 2),
                        "One of block contains more than 2 transaction")
        self.update_sys_param("max_tx_count ", str(max_tx_count))
