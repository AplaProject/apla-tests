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
        self.data = utils.login(url, prKey, 0)
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
        ecosysNum = "1"
        self.check_get_api("/ecosystemparams/?ecosystem="+ecosysNum, "", asserts)

    def test_get_param_current_ecosystem(self):
        asserts = ["list"]
        self.check_get_api("/ecosystemparams/", "", asserts)

    def test_get_params_ecosystem_with_names(self):
        asserts = ["list"]
        names = "founder_account,new_table,changing_tables"
        res = self.check_get_api("/ecosystemparams/?names="+names, "", asserts)
        mustBe = dict(count=3,
                      par1="founder_account",
                      par2="new_table",
                      par3="changing_tables")
        actual = dict(count=len(res["list"]),
                      par1=res["list"][0]["name"],
                      par2=res["list"][1]["name"],
                      par3=res["list"][2]["name"])
        self.assertDictEqual(actual, mustBe, "test_get_params_ecosystem_with_names is failed!")

    def test_get_parametr_of_current_ecosystem(self):
        asserts = ["id", "name", "value", "conditions"]
        data = {}
        self.check_get_api("/ecosystemparam/founder_account/", data, asserts)
        
    def test_get_incorrect_ecosys_parametr(self):
        asserts = ""
        error, message = self.get_error_api("/ecosystemparam/incorrectParam/", asserts)
        self.assertEqual(error, "E_PARAMNOTFOUND", "Incorrect error: " + error + message)

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
        self.assertDictEqual(dictNamesAPI, dictNames,
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

    def test_content_lang(self):
        nameLang = "Lang_" + utils.generate_random_name()
        data = {"ApplicationId": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        namePage = "Page_" + utils.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {"ApplicationId": 1, "Name": namePage, "Value": valuePage, "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("NewPage", dataPage)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = {"menu": 'default_menu', "menutree": [],
                   "tree": [{'tag': 'text', 'text': 'Hello, World_en'}],
                   "nodesCount": 1}
        contentRu = {"menu": 'default_menu', "menutree": [],
                     "tree": [{'tag': 'text', 'text': 'Hello, Мир_ru'}],
                   "nodesCount": 1}
        contentFr = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Monde_fr-FR'}],
                   "nodesCount": 1}
        contentDe = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Welt_de'}],
                   "nodesCount": 1}
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
                   "tree": [{'tag': 'text', 'text': 'Hello, World_en_ed'}],
                   "nodesCount": 1}
        contentRu = {"menu": 'default_menu', "menutree": [],
                     "tree": [{'tag': 'text', 'text': 'Hello, Мир_ru_ed'}],
                   "nodesCount": 1}
        contentFr = {"menu": 'default_menu', "menutree": [],
                       "tree": [{'tag': 'text', 'text': 'Hello, Monde_fr-FR_ed'}],
                   "nodesCount": 1}
        contentDe = {"menu": 'default_menu', "menutree": [],
                     "tree": [{'tag': 'text', 'text': 'Hello, Welt_de_ed'}],
                     "nodesCount": 1}
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

    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde": "true"}
        self.check_get_api("/table/contracts", data, asserts)

    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        #self.check_post_api("/vde/create", data, asserts)

    def is_node_owner_true(self):
        data = {}
        resp = utils.call_contract(url, prKey, "NodeOwnerCondition", data, token)
        status = utils.txstatus(url, pause, resp["hash"], token)
        self.assertGreater(int(status["blockid"]), 0,
                           "BlockId is not generated: " + str(status))
        
    def is_node_owner_false(self):
        keys = config.getKeys()
        prKey2 = keys["key1"]
        data2 = utils.login(url, prKey2, 0)
        token2 = data2["jwtToken"]
        data = {}
        resp = utils.call_contract(url, prKey2, "NodeOwnerCondition", data, token2)
        status = utils.txstatus(url, pause, resp["hash"], token2)
        self.assertEqual(status["errmsg"]["error"],
                         "Sorry, you do not have access to this action.",
                         "Incorrect message: " + str(status))
        
    def test_login(self):
        keys = config.getKeys()    
        data1 = utils.login(url, keys["key5"], 0)
        time.sleep(5)
        conf = config.getNodeConfig()
        res = utils.is_wallet_created(conf["1"]["dbHost"], conf["1"]["dbName"],
                                      conf["1"]["login"], conf["1"]["pass"],
                                      data1["key_id"])
        self.assertTrue(res, "Wallet for new user didn't created")
        
    def test_login2(self):
        isOne = False
        keys = config.getKeys() 
        data1 = utils.login(url, keys["key3"], 0)
        time.sleep(5)
        conf = config.getNodeConfig()
        res = utils.is_wallet_created(conf["1"]["dbHost"], conf["1"]["dbName"],
                                      conf["1"]["login"], conf["1"]["pass"],
                                      data1["key_id"])
        if res == True:
            data2 = utils.login(url, keys["key1"])
            time.sleep(5)
            isOne = utils.is_wallet_created(conf["1"]["dbHost"], conf["1"]["dbName"],
                                            conf["1"]["login"], conf["1"]["pass"],
                                            data2["key_id"])
            self.assertTrue(isOne, "Wallet for new user didn't created")

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
        self.assertIn("ws://", res, "Centrifugo is not connection to node!")

    def test_get_centrifugo_address_with_login(self):
        asserts = ["ws://"]
        data = ""
        res = self.check_get_api("/config/centrifugo", data, asserts)

    def test_content_hash(self):
        # 1. test with login
        # 2. test without login
        # 3. negative test without login
        def isHashNotEmpty(hash):
            hash = str(hash)
            if hash.find("{'hash':") != -1:
                return True
            else:
                return False
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Div(,Hello page!)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        asserts = ["hash"]
        authRes = self.check_post_api("/content/hash/" + name, "", asserts)
        notAuthRes = requests.post(url + "/content/hash/" + name)
        notAuthRes = notAuthRes.json()
        page = "not_exist_page_xxxxxxxxx"
        notAuthResNotExist = requests.post(url + "/content/hash/" + page)
        notAuthResNotExist = notAuthResNotExist.json()
        mustBe = dict(authRes=True,
                      notAuthRes=True,
                      msg="Page not found")
        actual = dict(authRes=isHashNotEmpty(authRes),
                      notAuthRes=isHashNotEmpty(notAuthRes),
                      msg=notAuthResNotExist["msg"])
        self.assertDictEqual(mustBe, actual, "Not all assertions passed in test_content_hash")

    def test_get_ecosystem_name(self):
        id = 1
        asserts = ["ecosystem_name"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts)

    def test_get_ecosystem_name_new(self):
        data = {"Name": "ecos_" + utils.generate_random_name()}
        res = self.call("NewEcosystem",data)
        id = self.check_get_api("/list/ecosystems", "", [])["count"]
        asserts = ["ecosystem_name"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts)

    def test_get_ecosystem_name_incorrect(self):
        id = 99999
        asserts = ["error"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts)


if __name__ == '__main__':
    unittest.main()
