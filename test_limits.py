import unittest
import json
import time

from conftest import setup_vars

from libs import actions
from libs import tools
from libs import db


class TestLimits():

    def setup_class(self):
        global token
        self.data = actions.login(setup_vars["conf"]["2"]["url"],
                                  setup_vars["conf"]["1"]['private_key'], 0)
        token = self.data["jwtToken"]
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, setup_vars, result, jwtToken):
        self.unit.assertIn("hash", result)
        hash = result['hash']
        status = actions.tx_status(setup_vars["conf"]["2"]["url"], setup_vars["wait"], hash, token)
        print("status tx: ", status)
        if int(status['blockid']) > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["error"]
        
    def call(self, name, data):
        resp = actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["conf"]["1"]['private_key'],
                                     name, data, token)
        res = self.assert_tx_in_block(setup_vars(), resp, token)
        return res
        
    def update_sys_param(self, param, value):
        data = {"Name": param, "Value" : value}
        res = self.call("UpdateSysParam", data)
        self.unit.assertGreater(int(res), 0,
                           "Block is not generated for updating sysparam: " +\
                           str(res))
        
    def test_max_tx_size(self, setup_vars):
        max_tx_size = db.get_system_parameter(setup_vars["conf"]["1"]["db"], "max_tx_size")
        self.update_sys_param("max_tx_size", "500")
        name = "cont" + tools.generate_random_name()
        code = "contract " + name + setup_vars["contract"]["limits"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.unit.assertEqual(error, "Max size of tx", "Incorrect error: " + error)
        self.update_sys_param("max_tx_size", str(max_tx_size))
        
    def test_max_block_size(self, setup_vars):
        max_block_size = db.get_system_parameter(setup_vars["conf"]["1"]["db"], "max_block_size")
        self.update_sys_param("max_block_size", "500")
        name = "cont" + tools.generate_random_name()
        code = "contract " + name + setup_vars["contract"]["limits"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.unit.assertEqual(error, "Max size of tx", "Incorrect error: " + error)
        self.update_sys_param("max_block_size", str(max_block_size))
        time.sleep(30)
      
    def test_max_block_user_tx(self, setup_vars):
        max_block_user_tx = db.get_system_parameter(setup_vars["conf"]["1"]["db"], "max_block_user_tx")
        self.update_sys_param("max_block_user_tx", "1")
        time.sleep(30)
        i = 1
        while i < 10: 
            name = "cont" + tools.generate_random_name()
            code = "contract " + name + setup_vars["contract"]["limits"]["code"]
            data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["conf"]["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = actions.get_max_block_id(setup_vars["conf"]["2"]["url"], token)
        print("maxBlock = ", maxBlock)
        isOneOrTwo = db.is_count_tx_in_block(setup_vars["conf"]["2"]["db"], maxBlock, 1)
        self.update_sys_param("max_block_user_tx ", str(max_block_user_tx ))
        time.sleep(30)
        self.unit.assertTrue(isOneOrTwo,
                        "One of block contains more than 2 transaction")
        
        
    def test_max_tx_count (self, setup_vars):
        max_tx_count = db.get_system_parameter(setup_vars["conf"]["1"]["db"], "max_tx_count")
        self.update_sys_param("max_tx_count", "2")
        i = 1
        while i < 10: 
            name = "cont" + tools.generate_random_name()
            code = "contract " + name + setup_vars["contract"]["limits"]["code"]
            data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            actions.call_contract(setup_vars["conf"]["2"]["url"], setup_vars["conf"]["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = actions.get_max_block_id(setup_vars["conf"]["2"]["url"], token)
        self.unit.assertTrue(db.is_count_tx_in_block(setup_vars["conf"]["2"]["db"], maxBlock, 2),
                        "One of block contains more than 2 transaction")
        self.update_sys_param("max_tx_count ", str(max_tx_count))
