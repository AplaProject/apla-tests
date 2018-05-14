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
        global url, token, prKey, pause,\
            dbHost, dbName, login, password, contractName, maxInt, minInt
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
        maxInt = 9223372036854775807
        minInt = -9223372036854775808
        #self.defaultValues = self.readDefaultParameters()

    def readDefaultParameters(self):
        path = os.path.join(os.getcwd(), "defaultSystemParameters.json")
        with open(path, 'r') as f:
            data = f.read()
        return json.loads(data)

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

    def test_ecosystem_price(self):
        name = "ecosystem_price"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "1000"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_contract_price(self):
        name = "contract_price"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "200"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_column_price(self):
        name = "column_price"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "200"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_table_price(self):
        name = "table_price"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "200"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_menu_price(self):
        name = "menu_price"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "100"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_page_price(self):
        name = "page_price"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "100"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_block_size(self):
        name = "max_block_size"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "67108864"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_tx_size(self):
        name = "max_tx_size"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "33554432"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_tx_count(self):
        name = "max_tx_count"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "1000"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_columns(self):
        name = "max_columns"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "50"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_indexes(self):
        name = "max_indexes"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "5"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_block_user_tx(self):
        name = "max_block_user_tx"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "100"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_fuel_tx(self):
        name = "max_fuel_tx"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "5952300"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "100000"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_max_fuel_block(self):
        name = "max_fuel_block"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "5952300"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": "100000"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_commission_size(self):
        name = "commission_size"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "5952300"}
        data7 = {"Name": name, "Value": str(maxInt)} #FAIL
        data8 = {"Name": name, "Value": "3"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = int(self.call(contractName, data5))
        count_res5 = int(self.getCountBlocks())
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=count_res5,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    # commission_wallet int64 - ?
    def test_commission_wallet(self):
        name = "commission_wallet"
        data1 = {"Name": name, "Value": str(minInt + (-1))}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "-1452.78"}
        data6 = {"Name": name, "Value": "0"}
        data7 = {"Name": name, "Value": "5952300"}
        data8 = {"Name": name, "Value": "-5958756388"}
        data9 = {"Name": name, "Value": str(minInt)}
        data10 = {"Name": name, "Value": str(maxInt)}
        data11 = {"Name": name, "Value": "3"}  # set default value
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = int(self.call(contractName, data6))
        count_res6 = int(self.getCountBlocks())
        res7 = int(self.call(contractName, data7))
        count_res7 = int(self.getCountBlocks())
        res8 = int(self.call(contractName, data8))
        count_res8 = int(self.getCountBlocks())
        res9 = int(self.call(contractName, data9))
        count_res9 = int(self.getCountBlocks())
        res10 = int(self.call(contractName, data10))
        count_res10 = int(self.getCountBlocks())
        res11 = int(self.call(contractName, data11))
        count_res11 = int(self.getCountBlocks())
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=count_res6,
                      res7=count_res7,
                      res8=count_res8,
                      res9=count_res9,
                      res10=count_res10,
                      res11=count_res11,)
        actual = dict(res1=res1,
                      res2=res2,
                      res3=res3,
                      res4=res4,
                      res5=res5,
                      res6=res6,
                      res7=res7,
                      res8=res8,
                      res9=res9,
                      res10=res10,
                      res11=res11,)
        print(mustBe)
        print(actual)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_1(self):
        name = "commission_wallet"
        data1 = {"Name": name, "Value": str(maxInt-1)}
        res = self.call(contractName, data1)
        print(res)
        #print(mustBe)
        #print(actual)

if __name__ == '__main__':
    unittest.main()
