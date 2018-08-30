import unittest
import utils
import config
import requests
import json
import funcs
import os
import time


class TestSystemParameters(unittest.TestCase):
    def setUp(self):
        global url, token, prKey, pause,\
            dbHost, dbName, login, password, contractName, maxInt, minInt, defaultValues, defaultValueKey
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]
        dbHost = self.config["2"]["dbHost"]
        dbName = self.config["2"]["dbName"]
        login = self.config["2"]["login"]
        password = self.config["2"]["pass"]
        contractName = "UpdateSysParam"
        maxInt = 9223372036854775807
        minInt = -9223372036854775808
        defaultValueKey = "system_parameters"
        defaultValues = self.readDefaultParameters()

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

    def create_contract(self, url, prKey):
        code,name = utils.generate_name_and_code("")
        data = {'Wallet': '', 'Value': code, "ApplicationId": 1,
                'Conditions': "ContractConditions(`MainCondition`)"}
        resp = utils.call_contract(url, prKey, "NewContract", data, self.data1["jwtToken"])
        return name

    def getCountBlocks(self):
        return utils.getCountTable(dbHost, dbName, login, password, "block_chain")

    def getSystemParameterValue(self, name):
        return utils.getSystemParameterValue(dbHost, dbName, login, password, name)



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
        data7 = {"Name": name, "Value": defaultValues[defaultValueKey][name]} # set default value
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

    # new_version_url

    def test_rb_blocks_1(self):
        name = "rb_blocks_1"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": "0"}
        data3 = {"Name": name, "Value": "1000"}
        data4 = {"Name": name, "Value": "hello"}
        data5 = {"Name": name, "Value": "1452.78"}
        data6 = {"Name": name, "Value": "999"}
        data7 = {"Name": name, "Value": defaultValues[defaultValueKey][name]} # set default value
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

    def test_full_nodes1(self):
        name = "full_nodes"
        data1 = {"Name": name, "Value": -1}
        data2 = {"Name": name, "Value": 0}
        data3 = {"Name": name, "Value": 1000}
        data4 = {"Name": name, "Value": "hello"}
        data5 = {"Name": name, "Value": 1452.78}
        data6 = {"Name": name, "Value": "[]"}
        data7 = {"Name": name, "Value": "[{}]"}
        data8 = {"Name": name, "Value": "[{},{}]"}
        data9 = {"Name": name, "Value":  "[{\"tcp_addr\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": \"193457000224851964\",\"public_key\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data10 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_addr\": \"http://127.0.0.1:7079\",\"key_id\": \"193457000224851964\",\"public_key\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data11 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_ident\": \"193457000224851964\",\"public_key\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data12 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": \"193457000224851964\",\"public_keyss\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data13 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": \"193457000224851964\",\"public_key\": \"e279dbdeb9207bb2a49937a5234\"},{\"tcp_address1\": \"127.0.0.1:7078\",\"api_address1\": \"http://127.0.0.1:7079\",\"key_id1\": \"193457000224851964\",\"public_key1\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data14 = {"Name": name, "Value": "[{\"tcp_address\": 100,\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": \"193457000224851964\",\"public_keyss\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data15 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": http://127.0.0.1:7079,\"key_id\": \"193457000224851964\",\"public_keyss\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data16 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": 1256.58,\"public_keyss\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data17 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": 193457000224851964,\"public_keyss\": \"e279dbdeb9207bb2a49937a5234\"}]"}
        data18 = {"Name": name, "Value": "[{\"tcp_address\": \"127.0.0.1:7078\",\"api_address\": \"http://127.0.0.1:7079\",\"key_id\": \"193457000224851964\",\"public_keyss\": 0}]"}
        res1 = self.call(contractName, data1)
        res2 = self.call(contractName, data2)
        res3 = self.call(contractName, data3)
        res4 = self.call(contractName, data4)
        res5 = self.call(contractName, data5)
        res6 = self.call(contractName, data6)
        res7 = self.call(contractName, data7)
        res8 = self.call(contractName, data8)
        res9 = self.call(contractName, data9)
        res10 = self.call(contractName, data10)
        res11 = self.call(contractName, data11)
        res12 = self.call(contractName, data12)
        res13 = self.call(contractName, data13)
        res14 = self.call(contractName, data14)
        res15 = self.call(contractName, data15)
        res16 = self.call(contractName, data16)
        res17 = self.call(contractName, data17)
        res18 = self.call(contractName, data18)
        msg = "Invalid value"
        mustBe = dict(res1=msg,
                      res2=msg,
                      res3=msg,
                      res4=msg,
                      res5=msg,
                      res6=msg,
                      res7=msg,
                      res8=msg,
                      res9=msg,
                      res10=msg,
                      res11=msg,
                      res12=msg,
                      res13=msg,
                      res14=msg,
                      res15=msg,
                      res16=msg,
                      res17=msg,
                      res18=msg)
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
                      res11=res11,
                      res12=res12,
                      res13=res13,
                      res14=res14,
                      res15=res15,
                      res16=res16,
                      res17=res17,
                      res18=res18)
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_full_nodes2(self):
        # Positive test for 3 nodes
        name = "full_nodes"
        par = self.getSystemParameterValue(name)
        parJson = json.loads(par)
        nodesCount = len(parJson)
        for i in parJson:
            if parJson[i]["tcp_address"] == "127.0.0.1:7080":
                parJson.pop(i)
        '''
        i = 0
        while i < nodesCount:
            if parJson[i]["tcp_address"] == "127.0.0.1:7080":
                parJson.pop(i)
                break
            i += 1
        '''
        parJson = json.dumps(parJson)
        data = {"Name": name, "Value": parJson}
        res = self.call(contractName, data)
        fullConfig = config.getNodeConfig()
        nodes = nodesCount - 1
        config1 = fullConfig["1"]
        config2 = fullConfig["2"]
        config3 = fullConfig["3"]
        db1 = config1["dbName"]
        db2 = config2["dbName"]
        db3 = config3["dbName"]
        login1 = config1["login"]
        login2 = config2["login"]
        login3 = config3["login"]
        pas1 = config1["pass"]
        pas2 = config2["pass"]
        pas3 = config3["pass"]
        host1 = config1["dbHost"]
        host2 = config2["dbHost"]
        host3 = config3["dbHost"]
        self.data1 = utils.login(config1["url"], config1['private_key'], 0)
        self.data2 = utils.login(config2["url"], config1['private_key'], 0)
        self.data3 = utils.login(config3["url"], config3['private_key'], 0)
        minBlockId1 = funcs.get_max_block_id(config1["url"], self.data1["jwtToken"])
        minBlockId2 = funcs.get_max_block_id(config2["url"], self.data2["jwtToken"])
        minBlockId3 = funcs.get_max_block_id(config3["url"], self.data3["jwtToken"])
        minBlockList = [minBlockId1, minBlockId2, minBlockId3]
        minBlock = int(max(minBlockList)) + 2
        ts_count = 20
        i = 1
        while i < ts_count:
            contName = self.create_contract(config1["url"], config1['private_key'])
            i = i + 1
            time.sleep(1)
        time.sleep(120)
        count_contracts1 = utils.getCountDBObjects(host1, db1, login1, pas1)["contracts"]
        count_contracts2 = utils.getCountDBObjects(host2, db2, login2, pas2)["contracts"]
        count_contracts3 = utils.getCountDBObjects(host3, db3, login3, pas3)["contracts"]
        maxBlockId1 = funcs.get_max_block_id(config1["url"], self.data1["jwtToken"])
        maxBlockId2 = funcs.get_max_block_id(config2["url"], self.data2["jwtToken"])
        maxBlockId3 = funcs.get_max_block_id(config3["url"], self.data3["jwtToken"])
        maxBlockList = [maxBlockId1, maxBlockId2, maxBlockId3]
        maxBlock = max(maxBlockList)
        hash1 = utils.get_blockchain_hash(host1, db1, login1, pas1, maxBlock)
        hash2 = utils.get_blockchain_hash(host2, db2, login2, pas2, maxBlock)
        hash3 = utils.get_blockchain_hash(host3, db3, login3, pas3, maxBlock)
        missingNode = utils.check_for_missing_node(host1, db1, login1, pas1, minBlock, maxBlock)
        dict1 = dict(count_contract=count_contracts1,
                     hash=str(hash1),
                     node_pos=str(missingNode))
        dict2 = dict(count_contract=count_contracts2,
                     hash=str(hash2),
                     node_pos="True")
        dict3 = dict(count_contract=count_contracts3,
                     hash=str(hash3),
                     node_pos="True")
        msg = "Test "+name+" is failed dict1 != dict2. contracts: \n"
        msg += str(count_contracts1) + str(hash1) + str(missingNode) + "\n"
        msg += str(count_contracts2) + str(hash2) + str(missingNode) + "\n"
        self.assertDictEqual(dict1, dict2, msg)
        msg = "Test " + name + " is failed dict1 != dict3. contracts: \n"
        msg += str(count_contracts1) + str(hash1) + str(missingNode) + "\n"
        msg += str(count_contracts3) + str(hash3) + str(missingNode) + "\n"
        self.assertDictEqual(dict1, dict3, msg)

    def test_number_of_nodes(self):
        name = "number_of_nodes"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": "0"}
        data3 = {"Name": name, "Value": "1000"}
        data4 = {"Name": name, "Value": "hello"}
        data5 = {"Name": name, "Value": "1452.78"}
        data6 = {"Name": name, "Value": "999"}
        data7 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    # blockchain_url

    def test_max_block_size(self):
        name = "max_block_size"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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



    # fuel_rate - ?

    def test_extend_cost_address_to_id(self):
        name = "extend_cost_address_to_id"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_id_to_address(self):
        name = "extend_cost_id_to_address"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt+1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_new_state(self):
        name = "extend_cost_new_state"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_sha256(self):
        name = "extend_cost_sha256"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_pub_to_id(self):
        name = "extend_cost_pub_to_id"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_ecosys_param(self):
        name = "extend_cost_ecosys_param"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_sys_param_string(self):
        name = "extend_cost_sys_param_string"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_sys_param_int(self):
        name = "extend_cost_sys_param_int"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_sys_fuel(self):
        name = "extend_cost_sys_fuel"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_validate_condition(self):
        name = "extend_cost_validate_condition"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_eval_condition(self):
        name = "extend_cost_eval_condition"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_has_prefix(self):
        name = "extend_cost_has_prefix"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_contains(self):
        name = "extend_cost_contains"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_replace(self):
        name = "extend_cost_replace"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_join(self):
        name = "extend_cost_join"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_update_lang(self):
        name = "extend_cost_update_lang"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_size(self):
        name = "extend_cost_size"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_substr(self):
        name = "extend_cost_substr"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_contracts_list(self):
        name = "extend_cost_contracts_list"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_is_object(self):
        name = "extend_cost_is_object"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_compile_contract(self):
        name = "extend_cost_compile_contract"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_flush_contract(self):
        name = "extend_cost_flush_contract"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_eval(self):
        name = "extend_cost_eval"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_len(self):
        name = "extend_cost_len"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_activate(self):
        name = "extend_cost_activate"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_deactivate(self):
        name = "extend_cost_deactivate"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_create_ecosystem(self):
        name = "extend_cost_create_ecosystem"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_table_conditions(self):
        name = "extend_cost_table_conditions"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_create_table(self):
        name = "extend_cost_create_table"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_perm_table(self):
        name = "extend_cost_perm_table"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_column_condition(self):
        name = "extend_cost_column_condition"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_create_column(self):
        name = "extend_cost_create_column"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_perm_column(self):
        name = "extend_cost_perm_column"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_extend_cost_json_to_map(self):
        name = "extend_cost_json_to_map"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_max_block_generation_time(self):
        name = "max_block_generation_time"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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

    def test_block_reward(self):
        name = "block_reward"
        data1 = {"Name": name, "Value": "-1"}
        data2 = {"Name": name, "Value": str(maxInt + 1)}
        data3 = {"Name": name, "Value": "hello"}
        data4 = {"Name": name, "Value": "1452.78"}
        data5 = {"Name": name, "Value": "0"}
        data6 = {"Name": name, "Value": "59523"}
        data7 = {"Name": name, "Value": str(maxInt)}
        data8 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
    #incorrect_blocks_per_day
    #node_ban_time
    #local_node_ban_time


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
        data11 = {"Name": name, "Value": defaultValues[defaultValueKey][name]}  # set default value
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
                      res11=count_res11, )
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
                      res11=res11, )
        self.assertDictEqual(mustBe, actual, name + " has problem!")

    def test_dbInsert_access_denied(self):
        value = """
        {
        data {}
        conditions {}
        action {
            DBInsert("system_parameters", "name,value,conditions", "my_param", "hello", "true")
            }
        }
        """
        code, name = utils.generate_name_and_code(value)
        data = {'Wallet': '', 'Value': code, "ApplicationId": 1,
                'Conditions': "ContractConditions(`MainCondition`)"}
        res = self.call("NewContract", data)
        mustBe = "system parameters access denied"
        res = self.call(name, "")
        self.assertEqual(mustBe, res, "test_dbInsert_access_denied has problem!")

    def test_dbUpdate_access_denied(self):
        value = """
        {
        data {}
        conditions {}
        action {
            DBUpdate("system_parameters", 1,"name,value,conditions", "my_param_upd", "hello_upd", "true")
            }
        }
        """
        code, name = utils.generate_name_and_code(value)
        data = {'Wallet': '', 'Value': code, "ApplicationId": 1,
                'Conditions': "ContractConditions(`MainCondition`)"}
        res = self.call("NewContract", data)
        mustBe = "system parameters access denied"
        res = self.call(name, "")
        self.assertEqual(mustBe, res, "test_dbUpdate_access_denied has problem!")

