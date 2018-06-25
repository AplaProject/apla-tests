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
        global url, token, prKey, pause, dbHost, dbName, login, pas
        self.config = config.getNodeConfig()
        url = self.config["1"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
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

    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    def assertMultiTxInBlock(self, result, jwtToken):
        self.assertIn("hashes", result)
        hashes = result['hashes']
        result = utils.txstatus_multi(url, pause, hashes, jwtToken)
        for status in result.values():
            self.assertNotIn('errmsg', status)
            self.assertGreater(int(status["blockid"]), 0, "BlockID not generated")


    def callMulti(self, name, data):
        resp = utils.call_multi_contract(url, prKey, name, data, token)
        resp = self.assertMultiTxInBlock(resp, token)
        return resp
    
    def waitBlockId(self, old_block_id, limit):
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
    def test_create_ecosystem(self):
        name = "Ecosys_" + utils.generate_random_name()
        data = {"Name": name}
        res = self.call("NewEcosystem", data)
        asserts = ["number"]
        ecosystemID = self.check_get_api("/ecosystems/", "", asserts)["number"]
        ecosystemTablesList = utils.getEcosysTablesById(dbHost, dbName, login, pas, ecosystemID)
        mustBe = dict(block = True,
                      tablesCount = 19)
        actual = dict(block=int(res)>0,
                      tablesCount=len(ecosystemTablesList))
        self.assertDictEqual(mustBe, actual, "test_create_ecosystem is failed!")


    def test_new_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_edit_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        id = funcs.get_application_id(url, name, token)
        data = {"ApplicationId": id, "Conditions": "false"}
        res = self.call("EditApplication", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_activate_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        id = funcs.get_application_id(url, name, token)
        dataDeact = {"ApplicationId": id, "Value": 0}
        res = self.call("DelApplication", dataDeact)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataAct = {"ApplicationId": id, "Value": 1}
        res = self.call("DelApplication", dataAct)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_export_application(self):
        name = "App" + utils.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        id = funcs.get_application_id(url, name, token)
        dataDeact = {"ApplicationId": id}
        res = self.call("ExportNewApp", dataDeact)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_new_ecosystem(self):
        name = "Ecos" + utils.generate_random_name()
        data = {"Name": name}
        res = self.call("NewEcosystem", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        
    def test_edit_ecosystem_name(self):
        id = 1
        newName = "Ecosys_"+utils.generate_random_name()
        data = {"EcosystemID": id, "NewName": newName}
        resBlockId = self.call("EditEcosystemName", data)
        asserts = ["list"]
        res = self.check_get_api("/list/ecosystems", "", asserts)
        # iterating response elements
        i=0
        requiredEcosysNameAPI=""
        while i < int(res['count']):
            if int(res['list'][i]['id']) == id:
                requiredEcosysNameAPI = res['list'][i]['name']
                break
            i+=1
        query="SELECT name FROM \"1_ecosystems\" WHERE id='"+str(id)+"'"
        requiredEcosysNameDB = utils.executeSQL(dbHost, dbName, login, pas, query)[0][0]
        mustBe = dict(block = True,
                      ecosysNameAPI = newName,
                      ecosysNameDB = newName)
        actual = dict(block = int(resBlockId)>0,
                      ecosysNameAPI = requiredEcosysNameAPI,
                      ecosysNameDB = requiredEcosysNameDB)
        self.assertDictEqual(mustBe, actual, "test_edit_ecosystem_name is failed!")

    def test_edit_ecosystem_name_incorrect_id(self):
        id = 500
        newName = "ecosys_"+utils.generate_random_name()
        data = {"EcosystemID": id, "NewName": newName}
        res = self.call("EditEcosystemName", data)
        self.assertEqual("Ecosystem "+str(id)+" does not exist", res)

    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "2999479990390000000"}
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
        countContracts = utils.getCountTable(dbHost, dbName, login, pas, "1_contracts")
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        asserts = ["name"]
        contractNameAPI = self.check_get_api("/contract/"+name, "", asserts)["name"]
        asserts = ["count"]
        countContractsAfter = self.check_get_api("/list/contracts", "", asserts)["count"]
        query = "SELECT name FROM \"1_contracts\" WHERE name='" + name + "'"
        contractName = utils.executeSQL(dbHost, dbName, login, pas, query)[0][0]
        mustBe = dict(block=True,
                      countContracts=int(countContracts + 1),
                      contractNameDB=name,
                      contractNameAPI="@1"+name)
        actual = dict(block=int(res)>0,
                      countContracts=int(countContractsAfter),
                      contractNameDB=contractName,
                      contractNameAPI=contractNameAPI)
        self.assertDictEqual(mustBe, actual, "test_new_contract is failed!")

    def test_new_contract_exists_name(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans = self.call("NewContract", data)
        msg = "Contract " + name + " already exists"
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
        query = "SELECT * FROM \"1_contracts\" WHERE name='" + name + "'"
        contractDataBefore = utils.executeSQL(dbHost, dbName, login, pas, query)
        conValBefore = str(contractDataBefore[0][1])
        data2 = {}
        data2["Id"] = funcs.get_contract_id(url, name, token)
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        res = self.call("EditContract", data2)
        end = url + "/contract/" + name
        ans = funcs.call_get_api(end, "", token)
        query = "SELECT * FROM \"1_contracts\" WHERE name='" + name + "'"
        contractData = utils.executeSQL(dbHost, dbName, login, pas, query)
        conID = contractData[0][0]
        conVal = str(contractData[0][1])
        conCond = contractData[0][6]
        mustBe = dict(block=True,
                      id=int(data2["Id"]),
                      val= conValBefore,
                      cond=data2["Conditions"],
                      wallet=newWallet)
        actual = dict(block=int(res)>0,
                      id=int(conID),
                      val=conVal,
                      cond=conCond,
                      wallet=ans["address"])
        self.assertDictEqual(mustBe, actual, "test_edit_contract is failed!")

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

    def test_new_parameter(self):
        countParamsBefore = utils.getCountTable(dbHost, dbName, login, pas, "1_parameters")
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        asserts = ["count"]
        paramsAPI = self.check_get_api("/list/parameters", "", asserts)
        countParamsAPI = paramsAPI["count"]
        i = 0
        while i < len(paramsAPI["list"]):
            if paramsAPI["list"][i]["name"] == name:
                paramNameAPI = paramsAPI["list"][i]["name"]
                paramValueAPI = paramsAPI["list"][i]["value"]
                paramCondAPI = paramsAPI["list"][i]["conditions"]
                break
            i+=1
        countParamsDB = utils.getCountTable(dbHost, dbName, login, pas, "1_parameters")
        query = "SELECT * FROM \"1_parameters\" WHERE name='" + name + "'"
        param = utils.executeSQL(dbHost, dbName, login, pas, query)
        paramNameDB = param[0][1]
        paramValueDB = param[0][2]
        paramCondDB = param[0][3]
        mustBe = dict(block=True,
                      countParamsAPI=int(countParamsBefore + 1),
                      countParamsDB=int(countParamsBefore + 1),
                      paramNameDB=name,
                      paramValueDB=data["Value"],
                      paramCondDB=data["Conditions"],
                      paramNameAPI=name,
                      paramValueAPI=data["Value"],
                      paramCondAPI=data["Conditions"])
        actual = dict(block=int(res)>0,
                      countParamsAPI=int(countParamsAPI),
                      countParamsDB=int(countParamsDB),
                      paramNameDB=paramNameDB,
                      paramValueDB=paramValueDB,
                      paramCondDB=paramCondDB,
                      paramNameAPI=paramNameAPI,
                      paramValueAPI=paramValueAPI,
                      paramCondAPI=paramCondAPI)
        self.assertDictEqual(mustBe, actual, "test_new_parameter is failed!")


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
        ans = self.call("EditParameter", data2)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_menu(self):
        countMenu = utils.getCountTable(dbHost, dbName, login, pas, "1_menu")
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        asserts = ["count"]
        countMenuAfterAPI = self.check_get_api("/list/menu", "", asserts)["count"]
        countMenuAfterDB = utils.getCountTable(dbHost, dbName, login, pas, "1_menu")
        query = "SELECT name FROM \"1_menu\" WHERE name='" + name + "'"
        menuNameDB = utils.executeSQL(dbHost, dbName, login, pas, query)[0][0]
        asserts = ["list"]
        menu = self.check_get_api("/list/menu", "", asserts)
        i = 0
        while i < len(menu["list"]):
            if menu["list"][i]["name"] == name:
                menuNameAPI = menu["list"][i]["name"]
                break
            i += 1
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        mustBe = dict(block=True,
                      countMenuAfterAPI=countMenu + 1,
                      countMenuAfterDB=countMenu + 1,
                      menuNameDB=name,
                      menuNameAPI=name,
                      content=content)
        actual = dict(block=int(res)>0,
                      countMenuAfterAPI=int(countMenuAfterAPI),
                      countMenuAfterDB=countMenuAfterDB,
                      menuNameDB=menuNameDB,
                      menuNameAPI=menuNameAPI,
                      content=mContent)
        self.assertDictEqual(mustBe, actual, "test_new_menu is failed!")

    def test_new_menu_exist_name(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        ans = self.call("NewMenu", data)
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
        asserts = ["list"]
        menu = self.check_get_api("/list/menu", "", asserts)
        i = 0
        while i < len(menu["list"]):
            if menu["list"][i]["name"] == name:
                menuNameAPI = menu["list"][i]["name"]
                menuValueAPI = menu["list"][i]["value"]
                menuConditionsAPI = menu["list"][i]["conditions"]
                break
            i += 1
        query = "SELECT * FROM \"1_menu\" WHERE name='" + name + "'"
        menu = utils.executeSQL(dbHost, dbName, login, pas, query)
        menuNameDB = menu[0][1]
        menuValueDB = menu[0][3]
        menuCondDB = menu[0][4]
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        mustBe = dict(block=True,
                      menuNameAPI=name,
                      menuValueAPI=dataEdit["Value"],
                      menuConditionsAPI=dataEdit["Conditions"],
                      menuNameDB=name,
                      menuValueDB=dataEdit["Value"],
                      menuCondDB=dataEdit["Conditions"],
                      content=content)
        actual = dict(block=int(res) > 0,
                      menuNameAPI=menuNameAPI,
                      menuValueAPI=menuValueAPI,
                      menuConditionsAPI=menuConditionsAPI,
                      menuNameDB=menuNameDB,
                      menuValueDB=menuValueDB,
                      menuCondDB=menuCondDB,
                      content=mContent)
        self.assertDictEqual(mustBe, actual, "test_new_menu is failed!")

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
        count = funcs.get_count(url, "menu", token)
        asserts = ["list"]
        menu = self.check_get_api("/list/menu", "", asserts)
        i = 0
        while i < len(menu["list"]):
            if menu["list"][i]["name"] == name:
                menuNameAPI = menu["list"][i]["name"]
                menuValueAPI = menu["list"][i]["value"]
                menuConditionsAPI = menu["list"][i]["conditions"]
                break
            i += 1
        query = "SELECT * FROM \"1_menu\" WHERE name='" + name + "'"
        menu = utils.executeSQL(dbHost, dbName, login, pas, query)
        menuNameDB = menu[0][1]
        menuValueDB = menu[0][3]
        menuCondDB = menu[0][4]
        content = {'tree': [{'tag': 'text', 'text': 'Item1\r\nAppendedItem'}]}
        mContent = funcs.get_content(url, "menu", name, "", 1, token)
        menuVal = data["Value"] + "\r\n"+ dataEdit["Value"]
        mustBe = dict(block=True,
                      menuNameAPI=name,
                      menuValueAPI=menuVal,
                      menuConditionsAPI=dataEdit["Conditions"],
                      menuNameDB=name,
                      menuValueDB=menuVal,
                      menuCondDB=dataEdit["Conditions"],
                      content=content)
        actual = dict(block=int(res) > 0,
                      menuNameAPI=menuNameAPI,
                      menuValueAPI=menuValueAPI,
                      menuConditionsAPI=menuConditionsAPI,
                      menuNameDB=menuNameDB,
                      menuValueDB=menuValueDB,
                      menuCondDB=menuCondDB,
                      content=mContent)
        self.assertDictEqual(mustBe, actual, "test_append_menu is failed!")

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
        content["nodesCount"] = 1
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
        content["nodesCount"] = 1
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
        content["nodesCount"] = 1
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
        content["nodesCount"] = 1
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
        res = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        res = self.call("EditBlock", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_edit_block_incorrect_condition(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = funcs.get_count(url, "blocks", token)
        condition = "tryam"
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": condition}
        ans = self.call("EditBlock", dataEdit)
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans, "Incorrect message: " + ans)

    def test_new_table(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"},{"name":"Myb","type":"json",
        "index": "0",  "conditions":"true"}, {"name":"MyD","type":"datetime",
        "index": "0",  "conditions":"true"}, {"name":"MyM","type":"money",
        "index": "0",  "conditions":"true"},{"name":"MyT","type":"text",
        "index": "0",  "conditions":"true"},{"name":"MyDouble","type":"double",
        "index": "0",  "conditions":"true"},{"name":"MyC","type":"character",
        "index": "0",  "conditions":"true"}]"""
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
        data["Permissions"] = per1 + per2 + per3
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataEdit = {}
        dataEdit["Name"] = name
        dataEdit["InsertPerm"] = "true"
        dataEdit["UpdatePerm"] = "true"
        dataEdit["NewColumnPerm"] = "true"
        res = self.call("EditTable", dataEdit)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_new_column(self):
        nameTab = "Tab_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameTab
        data["Columns"] = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        data["Permissions"] = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data["ApplicationId"] = 1
        res = self.call("NewTable", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        dataCol1 = {"TableName": nameTab, "Name": "var",
                   "Type": "varchar", "Index": "0", "Permissions": "true"}
        res1 = self.call("NewColumn", dataCol1)
        self.assertGreater(int(res1), 0, "BlockId is not generated: " + res1)
        dataCol2 = {"TableName": nameTab, "Name": "json",
                   "Type": "json", "Index": "0", "Permissions": "true"}
        res2 = self.call("NewColumn", dataCol2)
        self.assertGreater(int(res2), 0, "BlockId is not generated: " + res2)
        dataCol3 = {"TableName": nameTab, "Name": "num",
                   "Type": "number", "Index": "0", "Permissions": "true"}
        res3 = self.call("NewColumn", dataCol3)
        self.assertGreater(int(res3), 0, "BlockId is not generated: " + res3)
        dataCol4 = {"TableName": nameTab, "Name": "date",
                   "Type": "datetime", "Index": "0", "Permissions": "true"}
        res4 = self.call("NewColumn", dataCol4)
        self.assertGreater(int(res4), 0, "BlockId is not generated: " + res4)
        dataCol5 = {"TableName": nameTab, "Name": "sum",
                   "Type": "money", "Index": "0", "Permissions": "true"}
        res5 = self.call("NewColumn", dataCol5)
        self.assertGreater(int(res5), 0, "BlockId is not generated: " + res5)
        dataCol6 = {"TableName": nameTab, "Name": "name",
                   "Type": "text", "Index": "0", "Permissions": "true"}
        res6 = self.call("NewColumn", dataCol6)
        self.assertGreater(int(res6), 0, "BlockId is not generated: " + res6)
        dataCol7 = {"TableName": nameTab, "Name": "length",
                   "Type": "double", "Index": "0", "Permissions": "true"}
        res7 = self.call("NewColumn", dataCol7)
        self.assertGreater(int(res7), 0, "BlockId is not generated: " + res7)
        dataCol8 = {"TableName": nameTab, "Name": "code",
                   "Type": "character", "Index": "0", "Permissions": "true"}
        res8 = self.call("NewColumn", dataCol8)
        self.assertGreater(int(res8), 0, "BlockId is not generated: " + res8)

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
        data = {"AppID": 1, "Name": "Lang_" + utils.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
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

    def test_delayed_contracts(self):
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
        newLimit = 3
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
        self.waitBlockId(old_block_id, newLimit)
        # EditDelayedContract
        editLimit = 2
        data = {"Id":id, "Contract": contract_name, "EveryBlock": "1", "Conditions": "true", "Limit":editLimit}
        res = self.call("EditDelayedContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        old_block_id = int(res)
        # wait block_id until run CallDelayedContract
        self.waitBlockId(old_block_id, editLimit)
        # verify records count in table
        asserts = ["count"]
        res = self.check_get_api("/list/"+table_name, "", asserts)
        self.assertEqual(int(res["count"]), newLimit+editLimit)

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

    def test_update_system_parameters(self):
        data = {"Name": "max_block_user_tx", "Value" : "2"}
        res = self.call("UpdateSysParam", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

        
    def test_contract_memory_limit(self):
        # add contract with memory limit
        body = """
        {
        data {
            Count int "optional"
            }
        action {
            var a array
            while (true) {
                $Count = $Count + 1
                a[Len(a)] = JSONEncode(a)
                }
            }
        }
        """
        code, contract_name = utils.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # test
        data = ""
        msg = "Memory limit exceeded"
        res = self.call(contract_name, data)
        self.assertEqual(msg, res, "Incorrect message: " + res)

    def test_functions_recursive_limit(self):
        # add contract with recursive
        body = """
        {
        func myfunc(num int) int { 
            num = num + 1
            myfunc(num)
            }
        data{}
        conditions{}
        action {
            $a = 0
            myfunc($a)
            }
        }
        """
        code, contract_name = utils.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # test
        data = ""
        msg = "max call depth"
        res = self.call(contract_name, data)
        self.assertEqual(msg, res, "Incorrect message: " + res)

    def test_ei1_ExportNewApp(self):
        appID = 1
        data = {"ApplicationId": appID}
        res = self.call("ExportNewApp", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)

    def test_ei2_Export(self):
        appID = 1
        data = {}
        resExport = self.call("Export", data)
        founderID = utils.getFounderId(dbHost, dbName, login, pas)
        exportAppData = utils.getExportAppData(dbHost, dbName, login, pas, appID, founderID)
        jsonApp = str(exportAppData, encoding='utf-8')
        #res = self.check_get_api("/data/1_binaries/1/data/"+exportAppHash, "", "")
        #jsonApp = json.dumps(res)
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'w', encoding='UTF-8') as f:
            data = f.write(jsonApp)
        if os.path.exists(path):
            fileExist = True
        else:
            fileExist = False
        mustBe = dict(resultExport=True,
                      resultFile=True)
        actual = dict(resultExport=int(resExport)>0,
                      resultFile=fileExist)
        self.assertDictEqual(mustBe, actual, "test_Export is failed!")

    def test_ei3_ImportUpload(self):
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'r') as f:
            file = f.read()
        files = {'input_file': file}
        data = {}
        resp = utils.call_contract_with_files(url, prKey, "ImportUpload", data,
                                              files, token)
        resImportUpload = self.assertTxInBlock(resp, token)
        self.assertGreater(int(resImportUpload), 0, "BlockId is not generated: " + resImportUpload)

    def test_ei4_Import(self):
        founderID = utils.getFounderId(dbHost, dbName, login, pas)
        importAppData = utils.getImportAppData(dbHost, dbName, login, pas, founderID)
        importAppData = importAppData['data']
        contractName = "Import"
        data = [{"contract": contractName,
                 "params": importAppData[i]} for i in range(len(importAppData))]
        self.callMulti(contractName, data)

        
if __name__ == '__main__':
    unittest.main()
