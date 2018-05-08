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
        global url, token, prKey, pause
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url, prKey)
        token = self.data["jwtToken"]

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

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_post_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
        return result
            
    def get_error_api(self, endPoint, data):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    #################################################################

    #NewEcosystem
    def test_create_ecosystem(self):
        name = "Ecosys" + utils.generate_random_name()
        data = {"Name": name}
        res = self.call("NewEcosystem", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    #EditEcosystemName
    def test_edit_ecosystem_name(self):
        id = 1
        newName = "new_ecosystem_name_Andromeda"
        data = {"EcosystemID": id, "NewName": newName}
        res = self.call("EditEcosystemName", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        asserts = ["list"]
        res = self.check_get_api("/list/ecosystems", "", asserts)
        # iterating response elements
        i=0
        requiredEcosysName=""
        while i < int(res['count']):
            if int(res['list'][i]['id']) == id:
                requiredEcosysName = res['list'][i]['name']
            i+=1
        self.assertEqual(newName, requiredEcosysName)

    def test_edit_ecosystem_name_incorrect_id(self):
        id = 500
        newName = "ecosys_"+utils.generate_random_name()
        data = {"EcosystemID": id, "NewName": newName}
        res = self.call("EditEcosystemName", data)
        self.assertEqual("Ecosystem "+str(id)+" does not exist", res)

    #MoneyTransfer
    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "2999479990390000000000000"}
        res = self.call("MoneyTransfer", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_money_transfer_incorrect_wallet(self):
        wallet = "0005-2070-2000-0006"
        msg = "Recipient " + wallet + " is invalid"
        data = {"Recipient": wallet, "Amount": "1000"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans, msg, "Incorrect message" + msg)

    def test_money_transfer_zero_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "0"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans, msg, "Incorrect message" + msg)

    def test_money_transfer_negative_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "-1000"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans, msg, "Incorrect message" + msg)

    def test_money_transfer_amount_as_string(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "can't convert ttt to decimal"
        data = {"Recipient": wallet, "Amount": "ttt"}
        ans = self.call("MoneyTransfer", data)
        self.assertEqual(ans, msg, "Incorrect message" + msg)

    def test_money_transfer_with_comment(self):
        wallet = "0005-2070-2000-0006-0200"
        data = {"Recipient": wallet, "Amount": "1000", "Comment": "Test"}
        res = self.call("MoneyTransfer", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    #NewContract
    def test_new_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_new_contract_exists_name(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans = self.call("NewContract", data)
        msg = "Contract or function " + name + " exists"
        self.assertEqual(ans, msg, "Incorrect message: " + ans)

    def test_new_contract_without_name(self):
        code = "contract {data { }    conditions {    }    action {    }    }"
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        ans = self.call("NewContract", data)
        msg = "must be the name"
        self.assertIn(msg, ans, "Incorrect message: " + ans)

    def test_new_contract_incorrect_condition(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "condition"}
        ans = self.call("NewContract", data)
        msg = "unknown identifier condition"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    #EditContract
    def test_edit_contract_incorrect_condition(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        data2["Value"] = code
        data2["Conditions"] = "tryam"
        data2["WalletId"] = newWallet
        ans = self.call("EditContract", data2)
        msg = "unknown identifier tryam"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_contract_incorrect_condition1(self):
        newWallet = "0005"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        ans = self.call("EditContract", data2)
        msg = "New contract owner " + newWallet + " is invalid"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        res = self.call("EditContract", data2)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        end = url + "/contract/" + name
        ans = funcs.call_get_api(end, "", token)
        self.assertEqual(ans["address"], newWallet, "Wallet didn't change.")

    def test_edit_name_of_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        code1, name = utils.generate_name_and_code("")
        data2["Value"] = code1
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        msg = "Contracts or functions names cannot be changed"
        ans = self.call("EditContract", data2)
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_incorrect_contract(self):
        code, name = utils.generate_name_and_code("")
        newWallet = "0005-2070-2000-0006-0200"
        id = "9999"
        data2 = {}
        data2["Id"] = id
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        ans = self.call("EditContract", data2)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    #ActivateContract
    def test_activate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        id = funcs.get_contract_id(url, name, token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_activate_incorrect_contract(self):
        id = "9999"
        data = {"Id": id}
        ans = self.call("ActivateContract", data)
        msg = "Contract " + id + " does not exist"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    #DeactivateContract
    def test_deactivate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        id = funcs.get_contract_id(url, name, token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        res = self.call("DeactivateContract", data2)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_deactivate_incorrect_contract(self):
        id = "9999"
        data = {"Id": id}
        ans = self.call("DeactivateContract", data)
        msg = "Contract " + id + " does not exist"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    #NewParameter
    def test_new_parameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_new_parameter_exist_name(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        msg = "Parameter " + name + " already exists"
        ans = self.call("NewParameter", data)
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_parameter_incorrect_condition(self):
        condition = "tryam"
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewParameter", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    #EditParameter
    def test_edit_incorrect_parameter(self):
        newVal = "test_edited"
        id = "9999"
        data2 = {"Id": id, "Value": newVal, "Conditions": "true"}
        ans = self.call("EditParameter", data2)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_parameter_incorrect_condition(self):
        newVal = "test_edited"
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        id = funcs.get_parameter_id(url, name, token)
        condition = "tryam"
        data2 = {"Id": id, "Value": newVal, "Conditions": condition}
        ans = self.call("EditParameter", data2)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    



if __name__ == '__main__':
    unittest.main()
