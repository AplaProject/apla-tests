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

    def test_balance(self):
        asserts = ["amount", "money"]
        self.check_get_api('/balance/' + self.data['address'], "", asserts)
        
    def test_balance_incorrect_wallet(self):
        wallet = "0000-0990-3244-5453-2310"
        msg = "Wallet " + wallet + " is not valid"
        error, message = self.get_error_api('/balance/' + wallet, "")
        self.assertEqual(error, "E_INVALIDWALLET", "Incorrect error")

    def test_getEcosystem(self):
        asserts = ["number"]
        self.check_get_api("/ecosystems/", "", asserts)

    def test_get_param_ecosystem(self):
        asserts = ["list"]
        data = {'ecosystem': 1}
        self.check_get_api("/ecosystemparams/", data, asserts)

    def test_get_param_current_ecosystem(self):
        asserts = ["list"]
        self.check_get_api("/ecosystemparams/", "", asserts)

    def test_get_params_ecosystem_with_names(self):
        asserts = ["list"]
        data = {'ecosystem': 1, 'names': "name"}
        self.check_get_api("/ecosystemparams/", data, asserts)

    def test_get_parametr_of_current_ecosystem(self):
        asserts = ["id", "name", "value", "conditions"]
        data = {}
        self.check_get_api("/ecosystemparam/founder_account/", data, asserts)

    def test_get_tables_of_current_ecosystem(self):
        asserts = ["list", "count"]
        data = {}
        self.check_get_api("/tables", data, asserts)

    def test_get_table_information(self):
        dictNames = {}
        dictNamesAPI = {}
        data = {}
        tables = utils.getEcosysTables(self.config["1"]["dbHost"],
                                       self.config["1"]["dbName"],
                                       self.config["1"]["login"],
                                       self.config["1"]["pass"])
        for table in tables:
            if "table" not in table:
                tableInfo = funcs.call_get_api(url + "/table/" + table[2:], data, token)
                if "name" in str(tableInfo):
                    dictNames[table[2:]] = table[2:]
                    dictNamesAPI[table[2:]] = tableInfo["name"]
                else:
                    self.fail("Answer from API /table/" + table + " is: " + str(tableInfo))
        self.assertDictEqual(dictNames, dictNames,
                             "Any of API tableInfo gives incorrect data")
        
    def test_get_incorrect_table_information(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/table/" + table, data)
        err = "E_TABLENOTFOUND"
        msg = "Table " + table + " has not been found"
        self.assertEqual(err, error, "Incorrect error")
        self.assertEqual(message, msg, "Incorrect error massege")

    def test_get_table_data(self):
        dictCount = {}
        dictCountTable = {}
        data = {}
        tables = utils.getEcosysTables(self.config["1"]["dbHost"],
                                       self.config["1"]["dbName"],
                                       self.config["1"]["login"],
                                       self.config["1"]["pass"])
        for table in tables:
            tableData = funcs.call_get_api(url + "/list/" + table[2:], data, token)
            count = utils.getCountTable(self.config["1"]["dbHost"],
                                       self.config["1"]["dbName"],
                                       self.config["1"]["login"],
                                       self.config["1"]["pass"], table)
            if count > 0:
                if len(tableData["list"]) == count or (len(tableData["list"]) == 25 and
                                                       count > 25):
                    dictCount[table] = count
                    dictCountTable[table] = int(tableData["count"])
                else:
                    self.fail("Count list of " + table +\
                              " not equels of count table. Count of table: " +\
                              str(count) + " Count of list length: " +\
                              str(len(tableData["list"])))
            else:
                dictCount[table] = 0
                dictCountTable[table] = int(tableData["count"])
        self.assertDictEqual(dictCount, dictCountTable,
                             "Any of count not equels real count")  
        
    def test_get_incorrect_table_data(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/list/" + table, data)
        err = "E_TABLENOTFOUND"
        msg = "Table " + table + " has not been found"
        self.assertEqual(err, error, "Incorrect error")
        self.assertEqual(message, msg, "Incorrect error massege")

    def test_get_table_data_row(self):
        asserts = ["value"]
        data = {}
        self.check_get_api("/row/contracts/2", data, asserts)
        
    def test_get_incorrect_table_data_row(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/row/" + table + "/2", data)
        err = "E_QUERY"
        msg = "DB query is wrong"
        self.assertEqual(err, error, "Incorrect errror")
        self.assertEqual(msg, message, "Incorrect error message")

    def test_get_contract_information(self):
        asserts = ["name"]
        data = {}
        self.check_get_api("/contract/MainCondition", data, asserts)
        
    def test_get_incorrect_contract_information(self):
        contract = "contract"
        data = {}
        error, message = self.get_error_api("/contract/" + contract, data)
        err = "E_CONTRACT"
        msg = "There is not " + contract + " contract"

    def test_create_ecosystem(self):
        name = "Ecosys" + utils.generate_random_name()
        data = {"Name": name}
        res = self.call("NewEcosystem", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

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
        ans  = self.call("EditParameter", data2)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        self.assertEqual(mContent, content)
        
    def test_new_menu_exist_name(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans  = self.call("NewMenu", data)
        msg = "Menu " + name + " already exists"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_menu_incorrect_condition(self):
        name = "Menu_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewMenu", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        res = self.call("EditMenu", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        self.assertEqual(mContent, content)
        
    def test_edit_incorrect_menu(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "ItemEdited", "Conditions": "true"}
        ans = self.call("EditMenu", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_menu_incorrect_condition(self):
        name = "Menu_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": condition}
        ans = self.call("EditMenu", dataEdit)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_append_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        res = self.call("AppendMenu", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {'tree': [{'tag': 'text', 'text': 'Item1\r\nAppendedItem'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        self.assertEqual(mContent, content)
        
    def test_append_incorrect_menu(self):
        id = "999"
        dataEdit = {"Id": id, "Value": "AppendedItem", "Conditions": "true"}
        ans = self.call("AppendMenu", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_append_menu_incorrect_condition(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "menu", token)
        condition = "tryam"
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": condition}
        ans = self.call("AppendMenu", dataEdit)

    def test_new_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(cont, content)
        
    def test_new_page_exist_name(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"} 
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans = self.call("NewPage", data)
        msg = "Page " + name + " already exists"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_page_incorrect_condition(self):
        name = "Page_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition, "Menu": "default_menu"}
        ans = self.call("NewPage", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        res = self.call("EditPage", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(pContent, content)

    def test_edit_page_with_validate_count(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["ValidateCount"] = 6
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = "true"
        dataEdit["ValidateCount"] = 1
        dataEdit["Menu"] = "default_menu"
        res = self.call("EditPage", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(pContent, content)
        
    def test_edit_incorrect_page(self):
        id = "9999"
        dataEdit = {}
        dataEdit["Id"] = id
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        ans = self.call("EditPage", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_page_incorrect_condition(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        condition = "tryam"
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = condition
        dataEdit["Menu"] = "default_menu"
        ans = self.call("EditPage", dataEdit)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_append_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "pages", token)
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        res = self.call("AppendPage", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        pContent = funcs.get_content(url, "page", name, "", 1, token)
        self.assertEqual(pContent, content)
        
    def test_append_page_incorrect_id(self):
        id = "9999"
        dataEdit = {}
        dataEdit["Id"] = id
        dataEdit["Value"] = "Good by!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        ans = self.call("AppendPage", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_new_block_exist_name(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans = self.call("NewBlock", data)
        msg = "Block " + name + " already exists"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_block_incorrect_condition(self):
        name = "Block_" + utils.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewBlock", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_block_incorrect_id(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "Good by!", "Conditions": "true"}
        ans = self.call("EditBlock", dataEdit)
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res  = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        res = self.call("EditBlock", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_edit_block_incorrect_condition(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res  = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "blocks", token)
        condition = "tryam"
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": condition}
        ans = self.call("EditBlock", dataEdit)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_table(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_new_table_incorrect_condition1(self):
        data = {}
        data["Name"] = "Tab_" + utils.generate_random_name()
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        condition = "tryam"
        per1 = "{\"insert\": \"" + condition + "\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        ans = self.call("NewTable", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_table_incorrect_condition2(self):
        data = {}
        data["Name"] = "Tab_" + utils.generate_random_name()
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        condition = "tryam"
        per1 = "{\"insert\": \"true\","
        per2 = " \"update\" : \"" + condition + "\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        ans = self.call("NewTable", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_table_incorrect_condition3(self):
        data = {}
        data["Name"] = "Tab_" + utils.generate_random_name()
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        condition = "tryam"
        per1 = "{\"insert\": \"true\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"" + condition + "\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        ans = self.call("NewTable", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_table_exist_name(self):
        name = "tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans = self.call("NewTable", data)
        msg = "table " + name + " exists"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_new_table_identical_columns(self):
        name = "tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"},"
        col3 = "{\"name\":\"MyName\",\"type\":\"varchar\","
        col4 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2 + col3 + col4
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        ans = self.call("NewTable", data)
        msg = "There are the same columns"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_edit_table(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        dataEdit["Insert_con"] = "true"
        dataEdit["Columns"] = col1 + col2
        res = self.call("EditTable", dataEdit)
        print(res)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_edit_table_incorrect_condition1(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        per1 = "{\"insert\": \"" + condition + "\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        ans = self.call("NewTable", data)
        print(ans)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_table_incorrect_condition1(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        per1 = "{\"insert\": \"" + condition + "\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        ans = self.call("EditTable", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_table_incorrect_condition2(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        per1 = "{\"insert\": \"true\","
        per2 = " \"update\" : \"" + condition + "\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        ans = self.call("EditTable", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_table_incorrect_condition3(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        per1 = "{\"insert\": \"true\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"" + condition + "\"}"
        data["Permissions"] = per1 + per2 + per3
        ans = self.call("EditTable", data)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)
        
    def test_edit_table_identical_columns(self):
        name = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"},"
        col3 = "{\"name\":\"MyName\",\"type\":\"varchar\","
        col4 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        dataEdit["Columns"] = col1 + col2 + col3 + col4
        per1E = "{\"insert\": \"true\","
        per2E = " \"update\" : \"true\","
        per3E = " \"new_column\": \"true\"}"
        dataEdit["Permissions"] = per1E + per2E + per3E
        ans = self.call("EditTable", dataEdit)
        
    def test_edit_incorrect_table(self):
        name = "incorrect_name"
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        dataEdit["Columns"] = col1 + col2
        per1E = "{\"insert\": \"true\","
        per2E = " \"update\" : \"true\","
        per3E = " \"new_column\": \"true\"}"
        dataEdit["Permissions"] = per1E + per2E + per3E
        ans = self.call("EditTable", dataEdit)
        msg = "Table " + name + " has not been found"
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_column(self):
        nameTab = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameTab
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = nameTab
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        res = self.call("NewColumn", dataCol)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_edit_column(self):
        nameTab = "tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameTab
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = nameTab
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        res = self.call("NewColumn", dataCol)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {"TableName": nameTab, "Name": name, "Permissions": "false"}
        res = self.call("EditColumn", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_new_lang(self):
        data = {}
        data["AppID"] = 1
        data["Name"] = "Lang_" + utils.generate_random_name()
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        data["ApplicationId"] = 1
        res = self.call("NewLang", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_edit_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {}
        data["AppID"] = 1
        data["Name"] = name
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        data["ApplicationId"] = 1
        res = self.call("NewLang", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # Get last record in languages table
        asserts = ["count"]
        res = self.check_get_api("/list/languages", "", asserts)
        self.assertGreater(int(res["count"]), 0, "Count of languages not Greater 0: " + str(len(res["list"])))
        # Edit langRes
        dataEdit = {"Id": res["count"], "Name": name, "AppID": 1,
                    "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("EditLang", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_new_sign(self):
        name = "Sign_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        value = "{ \"forsign\" :\"" + name
        value += "\" ,  \"field\" :  \"" + name
        value += "\" ,  \"title\": \"" + name
        value += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data["Value"] = value
        data["Conditions"] = "true"
        res = self.call("NewSign", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_edit_sign(self):
        name = "Sign_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        value = "{ \"forsign\" :\"" + name
        value += "\" ,  \"field\" :  \"" + name
        value += "\" ,  \"title\": \"" + name
        value += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data["Value"] = value
        data["Conditions"] = "true"
        res = self.call("NewSign", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "signatures", token)
        dataEdit = {}
        dataEdit["Id"] = count
        valueE = "{ \"forsign\" :\"" + name
        valueE += "\" ,  \"field\" :  \"" + name
        valueE += "\" ,  \"title\": \"" + name
        valueE += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        dataEdit["Value"] = valueE
        dataEdit["Conditions"] = "true"
        res = self.call("EditSign", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_content_lang(self):
        nameLang = "Lang_" + utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        namePage = "Page_" + utils.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {"Name": namePage, "Value": valuePage, "ApplicationId": 1,
                    "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", dataPage)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {"menu": 'default_menu', "menutree": [],
                   "tree": [{'tag': 'text', 'text': 'Hello, World_en'}]}
        contentRu = {"menu": 'default_menu', "menutree": [],
                     "tree": [{'tag': 'text', 'text': 'Hello, Мир_ru'}]}
        contentFr = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Monde_fr-FR'}]}
        contentDe = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Welt_de'}]}
        dictExp ={"default" : content, "ru": contentRu,
                  "fr": contentFr, "de": contentDe, "pe": content}
        pContent = funcs.get_content(url, "page", namePage, "en", 1, token)          # should be: en
        ruPContent = funcs.get_content(url, "page", namePage, "ru", 1, token)      # should be: ru
        frPcontent = funcs.get_content(url, "page", namePage, "fr-FR", 1, token) # should be: fr-FR
        dePcontent = funcs.get_content(url, "page", namePage, "de-DE", 1, token)   # should be: de
        pePcontent = funcs.get_content(url, "page", namePage, "pe", 1, token)      # should be: en
        dictCur = {"default" : pContent, "ru": ruPContent,
                  "fr": frPcontent, "de": dePcontent, "pe": pePcontent}
        self.assertDictEqual(dictCur, dictExp, "One of langRes is faild")
        
    def test_content_lang_after_edit(self):
        nameLang = "Lang_" + utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        namePage = "Page_" + utils.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {"Name": namePage, "Value": valuePage, "Conditions": "true",
                    "Menu": "default_menu", "ApplicationId": 1,}
        res = self.call("NewPage", dataPage)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = self.check_get_api("/list/languages", "", [])["count"]
        dataEdit = {"Id": count, "AppID": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en_ed\", \"ru\" : \"Мир_ru_ed\"," +\
                "\"fr-FR\": \"Monde_fr-FR_ed\", \"de\": \"Welt_de_ed\"}"}
        res = self.call("EditLang", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {"menu": 'default_menu', "menutree": [],
                   "tree": [{'tag': 'text', 'text': 'Hello, World_en_ed'}]}
        contentRu = {"menu": 'default_menu', "menutree": [],
                     "tree": [{'tag': 'text', 'text': 'Hello, Мир_ru_ed'}]}
        contentFr = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Monde_fr-FR_ed'}]}
        contentDe = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Welt_de_ed'}]}
        dictExp ={"default" : content, "ru": contentRu,
                  "fr": contentFr, "de": contentDe, "pe": content}
        pContent = funcs.get_content(url, "page", namePage, "en", 1, token)          # should be: en
        ruPContent = funcs.get_content(url, "page", namePage, "ru", 1, token)      # should be: ru
        frPcontent = funcs.get_content(url, "page", namePage, "fr-FR", 1, token) # should be: fr-FR
        dePcontent = funcs.get_content(url, "page", namePage, "de-DE", 1, token)   # should be: de
        pePcontent = funcs.get_content(url, "page", namePage, "pe", 1, token)      # should be: en
        dictCur = {"default" : pContent, "ru": ruPContent,
                  "fr": frPcontent, "de": dePcontent, "pe": pePcontent}
        self.assertDictEqual(dictCur, dictExp, "One of langRes is faild")
        
    def test_update_system_parameters(self):
        data = {"Name": "max_block_user_tx", "Value" : "2"}
        res = self.call("UpdateSysParam", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_delayed_contracts(self):
        # func generate contract which return block_id and increment count blocks
        def waitBlockId(old_block_id, limit):
            while True:
                # add contract, which get block_id
                body = "{\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
                code, name = utils.generate_name_and_code(body)
                data = {"Value": code, "ApplicationId": 1,
                        "Conditions": "true"}
                res = self.call("NewContract", data)
                self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
                currrent_block_id = int(res)
                expected_block_id = old_block_id + limit + 1 # +1 spare block
                if currrent_block_id == expected_block_id:
                    break

        # add table for test
        column = """[{"name":"id_block","type":"number", "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "true", "update" : "true","new_column": "true"}"""
        table_name = "tab_delayed_" + utils.generate_random_name()
        data = {"Name": table_name,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

        # add contract which insert records in table in progress CallDelayedContract
        body = "{\n data{} \n conditions{} \n action { \n  DBInsert(\""+table_name+"\", \"id_block\", $block) \n } \n }"
        code, contract_name = utils.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

        # NewDelayedContract
        newLimit = 5
        data = {"Contract": contract_name, "EveryBlock": "1", "Conditions": "true", "Limit":newLimit}
        res = self.call("NewDelayedContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        old_block_id = int(res)

        # get record id of 'delayed_contracts' table for run EditDelayedContract
        asserts = ["count"]
        res = self.check_get_api("/list/delayed_contracts", "", asserts)
        count = len(res["list"])
        id = res["list"][0]["id"]
        i = 1
        while i < count:
            if res["list"][i]["id"] > id:
                id = res["list"][i]["id"]
            i = i + 1

        # wait block_id until run CallDelayedContract
        waitBlockId(old_block_id, newLimit)

        # EditDelayedContract
        editLimit = 4
        data = {"Id":id, "Contract": contract_name, "EveryBlock": "1", "Conditions": "true", "Limit":editLimit}
        res = self.call("EditDelayedContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        old_block_id = int(res)

        # wait block_id until run CallDelayedContract
        waitBlockId(old_block_id, editLimit)

        # verify records count in table
        asserts = ["count"]
        res = self.check_get_api("/list/"+table_name, "", asserts)
        self.assertEqual(int(res["count"]), newLimit+editLimit)
        
    def test_get_content_from_template(self):
        data = {}
        data["template"] = "SetVar(mytest, 100) Div(Body: #mytest#)"
        asserts = ["tree"]
        res = self.check_post_api("/content", data, asserts)
        answerTree = {'tree': [{'tag': 'div', 'children': [{'tag': 'text', 'text': '100'}]}]}
        self.assertEqual(answerTree, res)

    def test_get_content_from_template_empty(self):
        data = {}
        data["template"] = ""
        asserts = []
        res = self.check_post_api("/content", data, asserts)
        self.assertEqual(None, res)

    def test_get_content_from_template_source(self):
        data = {}
        data["template"] = "SetVar(mytest, 100) Div(Body: #mytest#)"
        data["source"] = "true"
        asserts = ["tree"]
        res = self.check_post_api("/content", data, asserts)
        answerTree = {'tree': [{'tag': 'setvar', 'attr': {'name': 'mytest', 'value': '100'}}, {'tag': 'div', 'children': [{'tag': 'text', 'text': '#mytest#'}]}]}
        self.assertEqual(answerTree, res)

    def test_get_content_from_template_source_empty(self):
        data = {}
        data["template"] = ""
        data["source"] = "true"
        asserts = []
        res = self.check_post_api("/content", data, asserts)
        self.assertEqual(None, res)

    def test_get_content_source(self):
        # Create new page for test
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "SetVar(a,\"Hello\") \n Div(Body: #a#)"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # Test
        asserts = ["tree"]
        res = self.check_post_api("/content/source/"+name, "", asserts)
        childrenText = res["tree"][1]["children"][0]["text"]
        self.assertEqual("#a#", childrenText)

    def test_get_content_source_empty(self):
        name = "default_page"
        asserts = ["tree"]
        res = self.check_post_api("/content/source/" + name, "", asserts)
        self.assertEqual(0, len(res["tree"]))

    def test_get_content_with_param_from_address_string(self):
        # Create new page for test
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "#test#"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # Test
        param = "?test="
        value = "hello123"
        asserts = ["tree"]
        res = self.check_post_api("/content/page/" + name + param + value, "", asserts)
        self.assertEqual(value, res["tree"][0]["text"])

    def test_get_back_api_version(self):
        asserts = ["."]
        data = ""
        self.check_get_api("/version", data, asserts)
        
    def test_get_systemparams_all_params(self):
        asserts = ["list"]
        res = self.check_get_api("/systemparams", "", asserts)
        self.assertGreater(len(res["list"]), 0, "Count of systemparams not Greater 0: " + str(len(res["list"])))

    def test_get_systemparams_some_param(self):
        asserts = ["list"]
        param = "gap_between_blocks"
        res = self.check_get_api("/systemparams/?names=" + param, "", asserts)
        self.assertEqual(1, len(res["list"]))
        self.assertEqual(param, res["list"][0]["name"])

    def test_get_systemparams_incorrect_param(self):
        asserts = ["list"]
        param = "not_exist_parameter"
        res = self.check_get_api("/systemparams/?names="+param, "", asserts)
        self.assertEqual(0, len(res["list"]))

    def test_get_contracts(self):
        limit = 25 # Default value without parameters
        asserts = ["list"]
        res = self.check_get_api("/contracts", "", asserts)
        self.assertEqual(limit, len(res["list"]))

    def test_get_contracts_limit(self):
        limit = 3
        asserts = ["list"]
        res = self.check_get_api("/contracts/?limit="+str(limit), "", asserts)
        self.assertEqual(limit, len(res["list"]))

    def test_get_contracts_offset(self):
        asserts = ["list"]
        res = self.check_get_api("/contracts", "", asserts)
        count = res["count"]
        offset = count
        res = self.check_get_api("/contracts/?offset=" + str(offset), "", asserts)
        self.assertEqual(None, res["list"])

    def test_get_contracts_empty(self):
        limit = 1000
        offset = 1000
        asserts = ["list"]
        res = self.check_get_api("/contracts/?limit="+str(limit)+"&offset="+str(offset), "", asserts)
        self.assertEqual(None, res["list"])

    def test_get_interface_page(self):
        asserts = ["id"]
        page = "default_page"
        res = self.check_get_api("/interface/page/"+page, "", asserts)
        self.assertEqual("default_page", res["name"])

    def test_get_interface_page_incorrect(self):
        asserts = ["error"]
        page = "not_exist_page_xxxxxxxxxxx"
        res = self.check_get_api("/interface/page/"+page, "", asserts)
        self.assertEqual("Page not found", res["msg"])

    def test_get_interface_menu(self):
        asserts = ["id"]
        menu = "default_menu"
        res = self.check_get_api("/interface/menu/"+menu, "", asserts)
        self.assertEqual("default_menu", res["name"])

    def test_get_interface_menu_incorrect(self):
        asserts = ["error"]
        menu = "not_exist_menu_xxxxxxxxxxx"
        res = self.check_get_api("/interface/menu/"+menu, "", asserts)
        self.assertEqual("Page not found", res["msg"])

    def test_get_interface_block(self):
        # Add new block
        block = "Block_" + utils.generate_random_name()
        data = {"Name": block, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # Test
        asserts = ["id"]
        res = self.check_get_api("/interface/block/"+block, "", asserts)
        self.assertEqual(block, res["name"])

    def test_get_interface_block_incorrect(self):
        asserts = ["error"]
        block = "not_exist_block_xxxxxxxxxxx"
        res = self.check_get_api("/interface/block/"+block, "", asserts)
        self.assertEqual("Page not found", res["msg"])

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

    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde": "true"}
        self.check_get_api("/table/contracts", data, asserts)

    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        #self.check_post_api("/vde/create", data, asserts)
        
    def test_upload_binary(self):
        name = "image_"+utils.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        res = self.assertTxInBlock(resp, token)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_new_app_param(self):
        name = "param_"+utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true" }
        res = self.call("NewAppParam", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_edit_app_param(self):
        name = "param_"+utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true" }
        res = self.call("NewAppParam", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data2 = {"Id": 1, "Name": name, "Value": "myParamEdited", "Conditions": "true" }
        res = self.call("EditAppParam", data2)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def is_node_owner_true(self):
        data = {}
        resp = utils.call_contract(url, prKey, "NodeOwnerCondition", data, token)
        status = utils.txstatus(url, pause, resp["hash"], token)
        self.assertGreater(int(status["blockid"]), 0,
                           "BlockId is not generated: " + str(status))
        
    def is_node_owner_false(self):
        keys = config.getKeys()
        prKey2 = keys["key1"]
        data2 = utils.login(url, prKey2)
        token2 = data2["jwtToken"]
        data = {}
        resp = utils.call_contract(url, prKey2, "NodeOwnerCondition", data, token2)
        status = utils.txstatus(url, pause, resp["hash"], token2)
        self.assertEqual(status["errmsg"]["error"],
                         "Sorry, you do not have access to this action.",
                         "Incorrect message: " + str(status))
        
    def test_login(self):
        keys = config.getKeys()    
        data1 = utils.login(url, keys["key1"])
        time.sleep(5)
        conf = config.getNodeConfig()
        res = utils.is_wallet_created(conf["1"]["dbHost"], conf["1"]["dbName"],
                                      conf["1"]["login"], conf["1"]["pass"],
                                      data1["key_id"])
        self.assertTrue(res, "Wallet for new user didn't created")

    def test_get_avatar_with_login(self):
        # add file in binaries
        name = "file_" + utils.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1, "DataMimeType":"image/jpeg"}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        res = self.assertTxInBlock(resp, token)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # find last added file
        asserts = ["count"]
        res = self.check_get_api("/list/binaries", "", asserts)
        lastRec = res["count"]
        # find founder ID
        asserts = ["list"]
        res = self.check_get_api("/list/members", "", asserts)
        # iterating response elements
        i = 0
        founderID = ""
        while i < len(res['list']):
            if res['list'][i]['member_name'] == "founder":
                founderID = res['list'][i]['id']
            i += 1
        # change column permissions
        data = {"TableName": "members", "Name":"image_id","Permissions": "true"}
        res = self.call("EditColumn", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # update members table
        code, name = utils.generate_name_and_code("{data{} conditions{} action{ DBUpdate(\"members\", "+founderID+",\"image_id\", "+lastRec+") } }")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data = {}
        resp = utils.call_contract(url, prKey, name, data, token)
        res = self.assertTxInBlock(resp, token)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # rollback changes column permissions
        data = {"TableName": "members", "Name":"image_id","Permissions": "ContractAccess(\"Profile_Edit\")"}
        res = self.call("EditColumn", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # test
        ecosystemID = "1"
        asserts = ""
        data = ""
        avaURL = url + "/avatar/" + ecosystemID + "/" + founderID
        res = funcs.call_get_api_with_full_response(avaURL, data, asserts)
        msg = "Content-Length is different!"
        self.assertIn("71926", str(res.headers["Content-Length"]),msg)

    def test_get_avatar_without_login(self):
        # add file in binaries
        name = "file_" + utils.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1, "DataMimeType":"image/jpeg"}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        res = self.assertTxInBlock(resp, token)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # find last added file
        asserts = ["count"]
        res = self.check_get_api("/list/binaries", "", asserts)
        lastRec = res["count"]
        # find founder ID
        asserts = ["list"]
        res = self.check_get_api("/list/members", "", asserts)
        # iterating response elements
        i = 0
        founderID = ""
        while i < len(res['list']):
            if res['list'][i]['member_name'] == "founder":
                founderID = res['list'][i]['id']
            i += 1
        # change column permissions
        data = {"TableName": "members", "Name":"image_id","Permissions": "true"}
        res = self.call("EditColumn", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # update members table
        code, name = utils.generate_name_and_code("{data{} conditions{} action{ DBUpdate(\"members\", "+founderID+",\"image_id\", "+lastRec+") } }")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data = {}
        resp = utils.call_contract(url, prKey, name, data, token)
        res = self.assertTxInBlock(resp, token)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # rollback changes column permissions
        data = {"TableName": "members", "Name":"image_id","Permissions": "ContractAccess(\"Profile_Edit\")"}
        res = self.call("EditColumn", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # test
        ecosystemID = "1"
        avaURL = url + "/avatar/" + ecosystemID + "/" + founderID
        resp = requests.get(avaURL)
        msg = "Content-Length is different!"
        self.assertIn("71926", str(resp.headers["Content-Length"]), msg)

    def test_get_centrifugo_address_without_login(self):
        resp = requests.get(url + '/config/centrifugo')
        res = resp.json()
        self.assertIn("http://", res, "Centrifugo is not connection to node!")

    def test_get_centrifugo_address_with_login(self):
        asserts = ["http://"]
        data = ""
        res = self.check_get_api("/config/centrifugo", data, asserts)

if __name__ == '__main__':
    unittest.main()
