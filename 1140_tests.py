import unittest
import utils
import config
import requests
import json
import funcs
import os
import time


class SystemContractsTestCase(unittest.TestCase):
    
    def setUp(self):
        global url, token, prKey, pause, dbHost, dbName, login, pas, msg
        self.config = config.getNodeConfig()
        url = self.config["1"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]
        msg = "'conditions' cannot call contracts or functions which can modify the blockchain database."


    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = utils.txstatus(url, pause, hash, jwtToken)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return {"blockid": int(status["blockid"]), "error": "0"}
        else:
            return {"blockid": 0, "error": status["errmsg"]["error"]}

    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    def callVDE(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        #resp = self.assertTxInBlock(resp, token)
        return resp

    def test_100(self):
        contractName = "recur_" + utils.generate_random_name()
        body = """
        {
        func runContract() int {
            var par map
            CallContract("%s", par)
            }
        data { }
        conditions { }
        action {
            runContract()
        }
        }
        """ % contractName
        code = utils.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contractName, "")
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_1(self):
        func_name = 'CreateColumn($r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_2(self):
        func_name = 'CreateTable($r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_3(self):
        func_name = 'DBInsert($r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_4(self):
        func_name = 'DBUpdate($r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_5(self):
        func_name = 'DBUpdateSysParam($r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_6(self):
        func_name = 'DBUpdateExt($r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_7(self):
        func_name = 'CreateEcosystem($r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_8(self):
        func_name = 'CreateContract($r,$r,$r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_9(self):
        func_name = 'UpdateContract($r,$r,$r,$r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_10(self):
        func_name = 'CreateLanguage($r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_11(self):
        func_name = 'EditLanguage($r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_12(self):
        func_name = 'Activate($r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_13(self):
        func_name = 'Deactivate($r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_14(self):
        func_name = 'EditEcosysName($r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_15(self):
        func_name = 'SetPubKey($r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_16(self):
        func_name = 'NewMoney($r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_17(self):
        func_name = 'UpdateNodesBan($r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

# VDE contracts *************************************************************************************
    def test_18(self):
        func_name = 'UpdateCron($r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.callVDE("NewContract", data)
        print(res)
        msg = 'cannot call contracts or functions which can modify the blockchain database'
        self.assertIn(msg, res['msg'], "Incorrect message: " + str(res))


    def test_19(self):
        func_name = 'CreateVDE($r,$r,$r,$r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.callVDE("NewContract", data)
        print(res)
        msg = 'cannot call contracts or functions which can modify the blockchain database'
        self.assertIn(msg, res['msg'], "Incorrect message: " + str(res))


    def test_20(self):
        func_name = 'DeleteVDE($r)'
        body = """
        {
            data { }
            conditions {
                %s
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.callVDE("NewContract", data)
        print(res)
        msg = 'cannot call contracts or functions which can modify the blockchain database'
        self.assertIn(msg, res['msg'], "Incorrect message: " + str(res))

# VDE contracts *************************************************************************************

    def test_21(self):
        func_name = 'UpdateNodesBan($r)'
        body = """
        {
            func runContract() int {
                %s
            }
            data { }
            conditions {
                runContract()
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_22(self):
        func_name = 'Deactivate($r,$r)'
        body = """
        {
            func runContract() int {
                %s
            }
            data { }
            conditions {
                runContract()
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_23(self):
        func_name = 'UpdateContract($r,$r,$r,$r,$r,$r,$r)'
        body = """
        {
            func runContract() int {
                %s
            }
            data { }
            conditions {
                runContract()
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_24(self):
        func_name = 'Println("hello")'
        body = """
        {
            func runContract() int {
                %s
            }
            data { }
            conditions {
                runContract()
            }
            action { }
        }
        """ % func_name
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertGreater(res["blockid"], 0, "Incorrect message: " + str(res))

    def test_25(self):
        body = """
        {
            func runContract string {
                return GetContractById(1)
            }
            data { }
            conditions {
                $a = runContract()
                $result = $a
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertGreater(res["blockid"], 0, "Incorrect message: " + str(res))

    def test_26(self):
        body = """
        {
            func runContract string {
                CallContract($r, $r1)
            }
            data { }
            conditions {
                runContract()
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_27(self):
        body = """
        {
            data { }
            conditions {
                CallContract($r, $r1)
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_28(self):
        body = """
        {
            data { }
            conditions {
                MainCondition($r,$r,$r)
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertGreater(res["blockid"], 0, "Incorrect message: " + str(res))

    def test_29(self):
        body = """
        {
            func myfunc {
                MainCondition($r,$r,$r)
            }
            data { }
            conditions {
                myfunc()
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertGreater(res["blockid"], 0, "Incorrect message: " + str(res))

    def test_30(self):
        # app basic
        body = """
        {
            data { }
            conditions {
                RolesAssign($r,$r)
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_31(self):
        body = """
        {
            func myfunc {
                DBInsert($r,$r)
            }
            data { }
            conditions {
                myfunc()
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_32(self):
        body = """
        {
            data { }
            conditions {
                DelColumn($r,$r)
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))


    def test_33(self):
        body = """
        {
            data { }
            conditions {
                DelTable($r)
            }
            action { }
        }
        """
        code = utils.generate_name_and_code(body)
        data = {
            "Value": code,
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewContract", data)
        print(res)
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

if __name__ == '__main__':
    unittest.main()
