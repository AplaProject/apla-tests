import unittest
import utils
import config
import requests
import json
import funcs
import os
import time


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        global url, token, prKey, pause, dbHost, dbName, login, password, contractName
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url, prKey)
        token = self.data["jwtToken"]
        dbHost = self.config["2"]["dbHost"]
        dbName = self.config["2"]["dbName"]
        login = self.config["2"]["login"]
        password = self.config["2"]["pass"]
        contractName = "UpdateSysParam"

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = utils.txstatus(url, pause, hash, jwtToken)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
        return result

    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    def getCountBlocks(self):
        return utils.getCountTable(dbHost, dbName, login, password, "block_chain")


    #default_ecosystem_page
    #default_ecosystem_menu
    #default_ecosystem_contract

    def test_gap_between_blocks(self):
        name = "gap_between_blocks"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": "0"}
        data3 = {"Name": name, "Value": "86400"}
        data4 = {"Name": name, "Value": "hello"}
        data5 = {"Name": name, "Value": "1452.78"}
        data6 = {"Name": name, "Value": "3"}
        data7 = {"Name": name, "Value": "2"} # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7)
        self.assertDictEqual(mustBe, actual, name+" has problem!")

    def test_rb_blocks_1(self):
        name = "rb_blocks_1"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": "0"}
        data3 = {"Name": name, "Value": "1000"}
        data4 = {"Name": name, "Value": "hello"}
        data5 = {"Name": name, "Value": "1452.78"}
        data6 = {"Name": name, "Value": "999"}
        data7 = {"Name": name, "Value": "60"} # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7)
        self.assertDictEqual(mustBe, actual, name+" has problem!")

    #full_nodes

    def test_number_of_nodes(self):
        name = "number_of_nodes"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": "0"}
        data3 = {"Name": name, "Value": "1000"}
        data4 = {"Name": name, "Value": "hello"}
        data5 = {"Name": name, "Value": "1452.78"}
        data6 = {"Name": name, "Value": "999"}
        data7 = {"Name": name, "Value": "101"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_1(self):
        name = "rb_blocks_1"
        data1 = {"Name": name, "Value": "-1"}
        res = self.call(contractName, data1)
        print(res)
        #print(mustBe)
        #print(actual)

if __name__ == '__main__':
    unittest.main()
