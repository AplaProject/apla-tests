import unittest
import utils
import config
import requests
import json
import funcs
import os
import time
from werkzeug.wsgi import responder


class LimitsTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        global conf, contract
        conf = config.getNodeConfig()
        contract = config.readFixtures("contracts")
    
    def setUp(self):
        global pause, token
        pause = conf["1"]["time_wait_tx_in_block"]
        self.data = utils.login(conf["1"]["url"],
                                conf["1"]['private_key'], 0)
        token = self.data["jwtToken"]        

    def assertTxInBlock(self, result, jwtToken):
        status = utils.txstatus(conf["1"]["url"], pause, result, token)
        print("status tx: ", status)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]
        
    def call(self, name, data):
        resp = utils.call_contract(conf["1"]["url"], conf["1"]['private_key'],
                                   name, data, token)
        if 'error' in resp:
            return resp
        else:
            res = self.assertTxInBlock(resp, token)
            return res
        
    def update_sys_param(self, param, value):
        data = {"Name": param, "Value" : value}
        res = self.call("UpdateSysParam", data)
        print(res)
        self.assertGreater(int(res), 0,
                           "Block is not generated for updating sysparam: " +\
                           res)
        
    def test_max_tx_size(self):
        max_tx_size = utils.get_system_parameter(conf["1"]["dbHost"],
                                                    conf["1"]["dbName"],
                                                    conf["1"]["login"],
                                                    conf["1"] ["pass"],
                                                    "max_tx_size")
        print("max_tx_size", max_tx_size)
        #500
        self.update_sys_param("max_tx_size", "450")
        print(funcs.call_get_api(conf["1"]["url"] + "/systemparams/?names=max_tx_size", "",
                                 token))
        name = "cont" + utils.generate_random_name()
        code = "contract " + name + contract["limits"]["code"]
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        print("error", error)
        self.assertIn("The size of tx is too big", error['msg'],
                      "Incorrect error: " + str(error))
        self.update_sys_param("max_tx_size", str(max_tx_size))
        
    def test_max_block_size(self):
        max_block_size = utils.get_system_parameter(conf["1"]["dbHost"],
                                                    conf["1"]["dbName"],
                                                    conf["1"]["login"],
                                                    conf["1"] ["pass"],
                                                    "max_block_size")
        self.update_sys_param("max_block_size", "450")
        name = "cont" + utils.generate_random_name()
        code = "contract " + name + contract["limits"]["code"]
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        error = self.call("NewContract", data)
        self.assertEqual(error, "stop generating block", "Incorrect error: " + error)
        self.update_sys_param("max_block_size", str(max_block_size))
        time.sleep(30)
      
    def test_max_block_user_tx(self):
        max_block_user_tx = utils.get_system_parameter(conf["1"]["dbHost"],
                                                    conf["1"]["dbName"],
                                                    conf["1"]["login"],
                                                    conf["1"] ["pass"],
                                                    "max_block_user_tx")
        self.update_sys_param("max_block_user_tx", "1")
        time.sleep(30)
        i = 1
        while i < 10: 
            name = "cont" + utils.generate_random_name()
            code = "contract " + name + contract["limits"]["code"]
            data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            utils.call_contract(conf["1"]["url"], conf["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = funcs.get_max_block_id(conf["1"]["url"], token)
        print("maxBlock = ", maxBlock)
        isOneOrTwo = utils.isCountTxInBlock(conf["1"]["dbHost"],
                                               conf["1"]["dbName"],
                                               conf["1"]["login"],
                                               conf["1"] ["pass"],
                                               maxBlock, 1)
        self.update_sys_param("max_block_user_tx", str(max_block_user_tx ))
        time.sleep(30)
        self.assertTrue(isOneOrTwo,
                        "One of block contains more than 2 transaction")
        
        
    def test_max_tx_count (self):
        max_tx_count = utils.get_system_parameter(conf["1"]["dbHost"],
                                                    conf["1"]["dbName"],
                                                    conf["1"]["login"],
                                                    conf["1"] ["pass"],
                                                    "max_tx_count")
        self.update_sys_param("max_tx_count", "2")
        print("here")
        i = 1
        while i < 10: 
            name = "cont" + utils.generate_random_name()
            code = "contract " + name + contract["limits"]["code"]
            data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
            utils.call_contract(conf["1"]["url"], conf["1"]['private_key'],
                                "NewContract", data, token)
            i = i + 1
        time.sleep(5)
        maxBlock = funcs.get_max_block_id(conf["1"]["url"], token)
        self.assertTrue(utils.isCountTxInBlock(conf["1"]["dbHost"],
                                               conf["1"]["dbName"],
                                               conf["1"]["login"],
                                               conf["1"] ["pass"],
                                               maxBlock, 2),
                        "One of block contains more than 2 transaction")
        print("here2")
        self.update_sys_param("max_tx_count", str(max_tx_count))


if __name__ == '__main__':
    unittest.main()