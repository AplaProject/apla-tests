import unittest
import requests
import json
import os
import time

from conftest import setup_vars

from libs import actions
from libs import tools
from libs import db



class TestApi():

    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, setup_vars, result, jwtToken):
        self.unit.assertIn("hash", result)
        hash = result['hash']
        status = actions.tx_status(setup_vars["url"], setup_vars["wait"], hash, jwtToken)
        if status['blockid'] > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys, setup_vars):
        end = setup_vars["url"] + endPoint
        result = actions.call_get_api(end, data, setup_vars["token"])
        for key in keys:
            self.unit.assertIn(key, result)
        return result

    def check_post_api(self, endPoint, data, keys, setup_vars):
        end = setup_vars["url"] + endPoint
        result = actions.call_post_api(end, data, setup_vars["token"])
        for key in keys:
            self.unit.assertIn(key, result)
        return result
            
    def get_error_api(self, endPoint, data, setup_vars):
        end = setup_vars["url"] + endPoint
        result = actions.call_get_api(end, data, setup_vars["token"])
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data, setup_vars):
        resp = actions.call_contract(setup_vars["url"], setup_vars["private_key"], name, data, setup_vars["token"])
        resp = self.assert_tx_in_block(resp, setup_vars["token"], setup_vars())
        return resp

    def test_balance(self):
        asserts = ["amount", "money"]
        self.check_get_api('/balance/' + self.data['address'], "", asserts, setup_vars())
        
    def test_balance_incorrect_wallet(self):
        wallet = "0000-0990-3244-5453-2310"
        msg = "Wallet " + wallet + " is not valid"
        error, message = self.get_error_api('/balance/' + wallet, "", setup_vars())
        self.unit.assertEqual(error, "E_INVALIDWALLET", "Incorrect error")

    def test_get_ecosystem(self):
        asserts = ["number"]
        self.check_get_api("/ecosystems/", "", asserts, setup_vars())

    def test_get_param_ecosystem(self):
        asserts = ["list"]
        ecosysNum = "1"
        self.check_get_api("/ecosystemparams/?ecosystem="+ecosysNum, "", asserts, setup_vars())

    def test_get_param_current_ecosystem(self):
        asserts = ["list"]
        self.check_get_api("/ecosystemparams/", "", asserts, setup_vars())

    def test_get_params_ecosystem_with_names(self):
        asserts = ["list"]
        names = "founder_account,new_table,changing_tables"
        res = self.check_get_api("/ecosystemparams/?names="+names, "", asserts, setup_vars())
        mustBe = dict(count=3,
                      par1="founder_account",
                      par2="new_table",
                      par3="changing_tables")
        actual = dict(count=len(res["list"]),
                      par1=res["list"][0]["name"],
                      par2=res["list"][1]["name"],
                      par3=res["list"][2]["name"])
        self.unit.assertDictEqual(actual, mustBe, "test_get_params_ecosystem_with_names is failed!")

    def test_get_parametr_of_current_ecosystem(self):
        asserts = ["id", "name", "value", "conditions"]
        data = {}
        self.check_get_api("/ecosystemparam/founder_account/", data, asserts, setup_vars())
        
    def test_get_incorrect_ecosys_parametr(self):
        asserts = ""
        error, message = self.get_error_api("/ecosystemparam/incorrectParam/", asserts, setup_vars())
        self.unit.assertEqual(error, "E_PARAMNOTFOUND", "Incorrect error: " + error + message)

    def test_get_tables_of_current_ecosystem(self):
        asserts = ["list", "count"]
        data = {}
        self.check_get_api("/tables", data, asserts, setup_vars())

    def test_get_table_information(self):
        dictNames = {}
        dictNamesAPI = {}
        data = {}
        tables = db.get_ecosys_tables(self.config["1"]["db"])
        for table in tables:
            if "table" not in table:
                tableInfo = actions.call_get_api(setup_vars["url"] + "/table/" + table[2:], data, setup_vars["token"])
                if "name" in str(tableInfo):
                    dictNames[table[2:]] = table[2:]
                    dictNamesAPI[table[2:]] = tableInfo["name"]
                else:
                    self.unit.fail("Answer from API /table/" + table + " is: " + str(tableInfo))
        self.unit.assertDictEqual(dictNamesAPI, dictNames,
                             "Any of API tableInfo gives incorrect data")
        
    def test_get_incorrect_table_information(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/table/" + table, data, setup_vars())
        err = "E_TABLENOTFOUND"
        msg = "Table " + table + " has not been found"
        self.unit.assertEqual(err, error, "Incorrect error")
        self.unit.assertEqual(message, msg, "Incorrect error massege")

    def test_get_table_data(self, setup_vars):
        dictCount = {}
        dictCountTable = {}
        data = {}
        tables = db.get_ecosys_tables(self.config["1"]["db"])
        for table in tables:
            tableData = actions.call_get_api(setup_vars["url"] + "/list/" + table[2:], data, setup_vars["token"])
            count = db.get_count_table(self.config["1"]["db"], table)
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
        self.unit.assertDictEqual(dictCount, dictCountTable,
                             "Any of count not equels real count")  
        
    def test_get_incorrect_table_data(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/list/" + table, data, setup_vars())
        err = "E_TABLENOTFOUND"
        msg = "Table " + table + " has not been found"
        self.unit.assertEqual(err, error, "Incorrect error")
        self.unit.assertEqual(message, msg, "Incorrect error massege")

    def test_get_table_data_row(self):
        asserts = ["value"]
        data = {}
        self.check_get_api("/row/contracts/2", data, asserts, setup_vars())
        
    def test_get_incorrect_table_data_row(self):
        table = "tab"
        data = {}
        error, message = self.get_error_api("/row/" + table + "/2", data, setup_vars())
        err = "E_QUERY"
        msg = "DB query is wrong"
        self.unit.assertEqual(err, error, "Incorrect errror")
        self.unit.assertEqual(msg, message, "Incorrect error message")

    def test_get_contract_information(self):
        asserts = ["name"]
        data = {}
        self.check_get_api("/contract/MainCondition", data, asserts, setup_vars())
        
    def test_get_incorrect_contract_information(self):
        contract = "contract"
        data = {}
        error, message = self.get_error_api("/contract/" + contract, data, setup_vars())
        err = "E_CONTRACT"
        msg = "There is not " + contract + " contract"

    def test_content_lang(self, setup_vars):
        nameLang = "Lang_" + tools.generate_random_name()
        data = {"ApplicationId": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        namePage = "Page_" + tools.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {"ApplicationId": 1, "Name": namePage, "Value": valuePage, "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("NewPage", dataPage, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = [{'tag': 'text', 'text': 'Hello, World_en'}]
        contentRu = [{'tag': 'text', 'text': 'Hello, Мир_ru'}]
        contentFr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR'}]
        contentDe = [{'tag': 'text', 'text': 'Hello, Welt_de'}]
        dictExp ={"default" : content, "ru": contentRu,
                  "fr": contentFr, "de": contentDe, "pe": content}
        pContent = actions.get_content(setup_vars["url"], "page", namePage, "en", 1, setup_vars["token"])     # should be: en
        ruPContent = actions.get_content(setup_vars["url"], "page", namePage, "ru", 1, setup_vars["token"])      # should be: ru
        frPcontent = actions.get_content(setup_vars["url"], "page", namePage, "fr-FR", 1, setup_vars["token"]) # should be: fr-FR
        dePcontent = actions.get_content(setup_vars["url"], "page", namePage, "de-DE", 1, setup_vars["token"])   # should be: de
        pePcontent = actions.get_content(setup_vars["url"], "page", namePage, "pe", 1, setup_vars["token"])      # should be: en
        dictCur = {"default" : pContent['tree'], "ru": ruPContent['tree'],
                  "fr": frPcontent['tree'], "de": dePcontent['tree'], "pe": pePcontent['tree']}
        self.unit.assertDictEqual(dictCur, dictExp, "One of langRes is faild")
        
    def test_content_lang_after_edit(self, setup_vars):
        nameLang = "Lang_" + tools.generate_random_name()
        data = {"ApplicationId": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        namePage = "Page_" + tools.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {"Name": namePage, "Value": valuePage, "Conditions": "true",
                    "Menu": "default_menu", "ApplicationId": 1,}
        res = self.call("NewPage", dataPage, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        count = self.check_get_api("/list/languages", "", [], setup_vars())["count"]
        dataEdit = {"Id": count, "AppID": 1, "Name": nameLang,
                "Trans": "{\"en\": \"World_en_ed\", \"ru\" : \"Мир_ru_ed\"," +\
                "\"fr-FR\": \"Monde_fr-FR_ed\", \"de\": \"Welt_de_ed\"}"}
        res = self.call("EditLang", dataEdit, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        content = [{'tag': 'text', 'text': 'Hello, World_en_ed'}]
        contentRu = [{'tag': 'text', 'text': 'Hello, Мир_ru_ed'}]
        contentFr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR_ed'}]
        contentDe = [{'tag': 'text', 'text': 'Hello, Welt_de_ed'}]
        dictExp ={"default" : content, "ru": contentRu,
                  "fr": contentFr, "de": contentDe, "pe": content}
        pContent = actions.get_content(setup_vars["url"], "page", namePage, "en", 1, setup_vars["token"])          # should be: en
        ruPContent = actions.get_content(setup_vars["url"], "page", namePage, "ru", 1, setup_vars["token"])      # should be: ru
        frPcontent = actions.get_content(setup_vars["url"], "page", namePage, "fr-FR", 1, setup_vars["token"]) # should be: fr-FR
        dePcontent = actions.get_content(setup_vars["url"], "page", namePage, "de-DE", 1, setup_vars["token"])   # should be: de
        pePcontent = actions.get_content(setup_vars["url"], "page", namePage, "pe", 1, setup_vars["token"])      # should be: en
        dictCur = {"default" : pContent['tree'], "ru": ruPContent['tree'],
                  "fr": frPcontent['tree'], "de": dePcontent['tree'], "pe": pePcontent['tree']}
        self.unit.assertDictEqual(dictCur, dictExp, "One of langRes is faild")

    def test_get_content_from_template(self):
        data = {}
        data["template"] = "SetVar(mytest, 100) Div(Body: #mytest#)"
        asserts = ["tree"]
        res = self.check_post_api("/content", data, asserts, setup_vars())
        answerTree = {'tree': [{'tag': 'div', 'children': [{'tag': 'text', 'text': '100'}]}]}
        self.unit.assertEqual(answerTree, res)

    def test_get_content_from_template_empty(self):
        data = {}
        data["template"] = ""
        asserts = []
        res = self.check_post_api("/content", data, asserts, setup_vars())
        self.unit.assertEqual(None, res)

    def test_get_content_from_template_source(self):
        data = {}
        data["template"] = "SetVar(mytest, 100) Div(Body: #mytest#)"
        data["source"] = "true"
        asserts = ["tree"]
        res = self.check_post_api("/content", data, asserts, setup_vars())
        answerTree = {'tree': [{'tag': 'setvar', 'attr': {'name': 'mytest', 'value': '100'}}, {'tag': 'div', 'children': [{'tag': 'text', 'text': '#mytest#'}]}]}
        self.unit.assertEqual(answerTree, res)

    def test_get_content_from_template_source_empty(self):
        data = {}
        data["template"] = ""
        data["source"] = "true"
        asserts = []
        res = self.check_post_api("/content", data, asserts, setup_vars())
        self.unit.assertEqual(None, res)

    def test_get_content_source(self):
        # Create new page for test
        name = "Page_" + tools.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "SetVar(a,\"Hello\") \n Div(Body: #a#)"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        asserts = ["tree"]
        res = self.check_post_api("/content/source/"+name, "", asserts, setup_vars())
        childrenText = res["tree"][1]["children"][0]["text"]
        self.unit.assertEqual("#a#", childrenText)

    def test_get_content_with_param_from_address_string(self):
        # Create new page for test
        name = "Page_" + tools.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "#test#"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        param = "?test="
        value = "hello123"
        asserts = ["tree"]
        res = self.check_post_api("/content/page/" + name + param + value, "", asserts, setup_vars())
        self.unit.assertEqual(value, res["tree"][0]["text"])

    def test_get_content_from_another_ecosystem(self, setup_vars):
        # create new ecosystem
        ecosysName = "Ecosys_" + tools.generate_random_name()
        data = {"Name": ecosysName}
        res = self.call("NewEcosystem", data, setup_vars())
        self.unit.assertGreater(int(res), 0,
                           "BlockId is not generated: " + str(res))
        ecosysNum = actions.call_get_api(setup_vars["url"] + "/ecosystems/", "", setup_vars["token"])["number"]
        # login founder in new ecosystem
        data2 = actions.login(setup_vars["url"], setup_vars["private_key"], 0, ecosysNum)
        token2 = data2["jwtToken"]
        # create page in new ecosystem
        pageName = "Page_" + tools.generate_random_name()
        pageText = "Page in "+str(ecosysNum)+" ecosystem"
        pageValue = "Span("+pageText+")"
        data = {"Name": pageName, "Value": pageValue, "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        resp = actions.call_contract(setup_vars["url"], setup_vars["private_key"], "@1NewPage", data, token2)
        status = actions.tx_status(setup_vars["url"], setup_vars["wait"], resp["hash"], token2)
        self.unit.assertGreater(int(status["blockid"]), 0,"BlockId is not generated: " + str(status))
        # create menu in new ecosystem
        menuName = "Menu_" + tools.generate_random_name()
        menuTitle = "Test menu"
        data = {"Name": menuName, "Value": "MenuItem(Title:\""+menuTitle+"\")", "ApplicationId": 1,
                "Conditions": "true"}
        resp = actions.call_contract(setup_vars["url"], setup_vars["private_key"], "@1NewMenu", data, token2)
        status = actions.tx_status(setup_vars["url"], setup_vars["wait"], resp["hash"], token2)
        self.unit.assertGreater(int(status["blockid"]), 0, "BlockId is not generated: " + str(status))
        # test
        data = ""
        asserts = ["tree"]
        resPage = self.check_post_api("/content/page/@" + str(ecosysNum) + pageName, data, asserts, setup_vars())
        resMenu = self.check_post_api("/content/menu/@" + str(ecosysNum) + menuName, data, asserts, setup_vars())
        mustBe = dict(pageText=pageText,
                      menu=menuTitle)
        expectedValue = dict(pageText=resPage["tree"][0]["children"][0]["text"],
                      menu=resMenu["tree"][0]["attr"]["title"])
        self.unit.assertEqual(mustBe, expectedValue, "Dictionaries are different!")

    def test_get_back_api_version(self):
        asserts = ["."]
        data = ""
        self.check_get_api("/version", data, asserts, setup_vars())
        
    def test_get_systemparams_all_params(self):
        asserts = ["list"]
        res = self.check_get_api("/systemparams", "", asserts, setup_vars())
        self.unit.assertGreater(len(res["list"]), 0, "Count of systemparams not Greater 0: " + str(len(res["list"])))

    def test_get_systemparams_some_param(self):
        asserts = ["list"]
        param = "gap_between_blocks"
        res = self.check_get_api("/systemparams/?names=" + param, "", asserts, setup_vars())
        self.unit.assertEqual(1, len(res["list"]))
        self.unit.assertEqual(param, res["list"][0]["name"])

    def test_get_systemparams_incorrect_param(self):
        asserts = ["list"]
        param = "not_exist_parameter"
        res = self.check_get_api("/systemparams/?names="+param, "", asserts, setup_vars())
        self.unit.assertEqual(0, len(res["list"]))

    def test_get_contracts(self):
        limit = 25 # Default value without parameters
        asserts = ["list"]
        res = self.check_get_api("/contracts", "", asserts, setup_vars())
        self.unit.assertEqual(limit, len(res["list"]))

    def test_get_contracts_limit(self):
        limit = 3
        asserts = ["list"]
        res = self.check_get_api("/contracts/?limit="+str(limit), "", asserts, setup_vars())
        self.unit.assertEqual(limit, len(res["list"]))

    def test_get_contracts_offset(self):
        asserts = ["list"]
        res = self.check_get_api("/contracts", "", asserts, setup_vars())
        count = res["count"]
        offset = count
        res = self.check_get_api("/contracts/?offset=" + str(offset), "", asserts, setup_vars())
        self.unit.assertEqual(None, res["list"])

    def test_get_contracts_empty(self):
        limit = 1000
        offset = 1000
        asserts = ["list"]
        res = self.check_get_api("/contracts/?limit="+str(limit)+"&offset="+str(offset), "", asserts, setup_vars())
        self.unit.assertEqual(None, res["list"])

    def test_get_interface_page(self):
        asserts = ["id"]
        page = "default_page"
        res = self.check_get_api("/interface/page/"+page, "", asserts, setup_vars())
        self.unit.assertEqual("default_page", res["name"])

    def test_get_interface_page_incorrect(self):
        asserts = ["error"]
        page = "not_exist_page_xxxxxxxxxxx"
        res = self.check_get_api("/interface/page/"+page, "", asserts, setup_vars())
        self.unit.assertEqual("Page not found", res["msg"])

    def test_get_interface_menu(self):
        asserts = ["id"]
        menu = "default_menu"
        res = self.check_get_api("/interface/menu/"+menu, "", asserts, setup_vars())
        self.unit.assertEqual("default_menu", res["name"])

    def test_get_interface_menu_incorrect(self):
        asserts = ["error"]
        menu = "not_exist_menu_xxxxxxxxxxx"
        res = self.check_get_api("/interface/menu/"+menu, "", asserts, setup_vars())
        self.unit.assertEqual("Page not found", res["msg"])

    def test_get_interface_block(self):
        # Add new block
        block = "Block_" + tools.generate_random_name()
        data = {"Name": block, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        asserts = ["id"]
        res = self.check_get_api("/interface/block/"+block, "", asserts, setup_vars())
        self.unit.assertEqual(block, res["name"])

    def test_get_interface_block_incorrect(self):
        asserts = ["error"]
        block = "not_exist_block_xxxxxxxxxxx"
        res = self.check_get_api("/interface/block/"+block, "", asserts, setup_vars())
        self.unit.assertEqual("Page not found", res["msg"])

    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde": "true"}
        self.check_get_api("/table/contracts", data, asserts, setup_vars())

    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        #self.check_post_api("/vde/create", data, asserts)

    def is_node_owner_true(self, setup_vars):
        data = {}
        resp = actions.call_contract(setup_vars["url"], setup_vars["private_key"], "NodeOwnerCondition", data, setup_vars["token"])
        status = actions.tx_status(setup_vars["url"], setup_vars["wait"], resp["hash"], setup_vars["token"])
        self.unit.assertGreater(int(status["blockid"]), 0,
                           "BlockId is not generated: " + str(status))
        
    def is_node_owner_false(self, setup_vars):
        keys = tools.read_config("keys")
        prKey2 = keys["key1"]
        data2 = actions.login(setup_vars["url"], prKey2, 0)
        token2 = data2["jwtToken"]
        data = {}
        resp = actions.call_contract(setup_vars["url"], prKey2, "NodeOwnerCondition", data, token2)
        status = actions.tx_status(setup_vars["url"], setup_vars["wait"], resp["hash"], token2)
        self.unit.assertEqual(status["errmsg"]["error"],
                         "Sorry, you do not have access to this action.",
                         "Incorrect message: " + str(status))
        
    def test_login(self):
        keys = tools.read_fixtures("keys")
        data1 = actions.login(setup_vars["url"], keys["key5"], 0)
        time.sleep(5)
        conf = tools.read_config("nodes")
        res = db.is_wallet_created(conf["1"]["db"], data1["key_id"])
        self.unit.assertTrue(res, "Wallet for new user didn't created")
        
    def test_login2(self):
        isOne = False
        keys = tools.read_fixtures("keys")
        data1 = actions.login(setup_vars["url"], keys["key3"], 0)
        time.sleep(5)
        conf = tools.read_config("nodes")
        res = db.is_wallet_created(conf["1"]["db"], data1["key_id"])
        if res == True:
            data2 = actions.login(setup_vars["url"], keys["key1"], 0)
            time.sleep(5)
            isOne = db.is_wallet_created(conf["1"]["db"], data2["key_id"])
            self.unit.assertTrue(isOne, "Wallet for new user didn't created")

    def test_get_avatar_with_login(self):
        # add file in binaries
        name = "file_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1, "DataMimeType":"image/jpeg"}
        resp = actions.call_contract_with_files(setup_vars["url"], setup_vars["private_key"], "UploadBinary", data,
                                                files, setup_vars["token"])
        res = self.assert_tx_in_block(resp, setup_vars["token"], setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # find last added file
        asserts = ["count"]
        res = self.check_get_api("/list/binaries", "", asserts, setup_vars())
        lastRec = res["count"]
        # find founder ID
        asserts = ["list"]
        res = self.check_get_api("/list/members", "", asserts, setup_vars())
        # iterating response elements
        i = 0
        founderID = ""
        while i < len(res['list']):
            if res['list'][i]['member_name'] == "founder":
                founderID = res['list'][i]['id']
            i += 1
        # change column permissions
        data = {"TableName": "members",
                "Name":"image_id",
                "UpdatePerm": "true",
                "ReadPerm": "true"}
        res = self.call("EditColumn", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # update members table
        code = """
        {
            data{}
            conditions{}
            action{
                DBUpdate("members", %s, {image_id: "%s"})
            }
        }
        """ % (founderID, lastRec)
        code, name = tools.generate_name_and_code(code)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data = {}
        resp = actions.call_contract(setup_vars["url"], setup_vars["private_key"], name, data, setup_vars["token"])
        res = self.assert_tx_in_block(resp, setup_vars["token"], setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # rollback changes column permissions
        data = {"TableName": "members",
                "Name":"image_id",
                "UpdatePerm": "ContractAccess(\"Profile_Edit\")",
                "ReadPerm": "true"}
        res = self.call("EditColumn", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # test
        ecosystemID = "1"
        asserts = ""
        data = ""
        avaURL = setup_vars["url"] + "/avatar/" + ecosystemID + "/" + founderID
        res = actions.call_get_api_with_full_response(avaURL, data, asserts)
        msg = "Content-Length is different!"
        self.unit.assertIn("71926", str(res.headers["Content-Length"]),msg)

    def test_get_avatar_without_login(self):
        # add file in binaries
        name = "file_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1, "DataMimeType":"image/jpeg"}
        resp = actions.call_contract_with_files(setup_vars["url"], setup_vars["private_key"], "UploadBinary", data,
                                                files, setup_vars["token"])
        res = self.assert_tx_in_block(resp, setup_vars["token"], setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # find last added file
        asserts = ["count"]
        res = self.check_get_api("/list/binaries", "", asserts, setup_vars())
        lastRec = res["count"]
        # find founder ID
        asserts = ["list"]
        res = self.check_get_api("/list/members", "", asserts, setup_vars())
        # iterating response elements
        i = 0
        founderID = ""
        while i < len(res['list']):
            if res['list'][i]['member_name'] == "founder":
                founderID = res['list'][i]['id']
            i += 1
        # change column permissions
        data = {"TableName": "members",
                "Name": "image_id",
                "UpdatePerm": "true",
                "ReadPerm": "true"}
        res = self.call("EditColumn", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # update members table
        code = """
               {
                   data{}
                   conditions{}
                   action{
                       DBUpdate("members", %s, {image_id: "%s"})
                   }
               }
               """ % (founderID, lastRec)
        code, name = tools.generate_name_and_code(code)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        data = {}
        resp = actions.call_contract(setup_vars["url"], setup_vars["private_key"], name, data, setup_vars["token"])
        res = self.assert_tx_in_block(resp, setup_vars["token"], setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # rollback changes column permissions
        data = {"TableName": "members",
                "Name":"image_id",
                "UpdatePerm": "ContractAccess(\"Profile_Edit\")",
                "ReadPerm": "true"}
        res = self.call("EditColumn", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + res)
        # test
        ecosystemID = "1"
        avaURL = setup_vars["url"] + "/avatar/" + ecosystemID + "/" + founderID
        resp = requests.get(avaURL)
        msg = "Content-Length is different!"
        self.unit.assertIn("71926", str(resp.headers["Content-Length"]), msg)

    def test_get_centrifugo_address_without_login(self):
        resp = requests.get(setup_vars["url"] + '/config/centrifugo')
        res = resp.json()
        self.unit.assertIn("ws://", res, "Centrifugo is not connection to node!")

    def test_get_centrifugo_address_with_login(self):
        asserts = ["ws://"]
        data = ""
        res = self.check_get_api("/config/centrifugo", data, asserts, setup_vars())

    def test_content_hash(self):
        # 1. test with login
        # 2. test without login
        # 3. negative test without login
        def is_hash_not_empty(hash):
            hash = str(hash)
            if hash.find("{'hash':") != -1:
                return True
            else:
                return False
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Div(,Hello page!)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        asserts = ["hash"]
        authRes = self.check_post_api("/content/hash/" + name, "", asserts, setup_vars())
        notAuthRes = requests.post(setup_vars["url"] + "/content/hash/" + name)
        notAuthRes = notAuthRes.json()
        page = "not_exist_page_xxxxxxxxx"
        notAuthResNotExist = requests.post(setup_vars["url"] + "/content/hash/" + page)
        notAuthResNotExist = notAuthResNotExist.json()
        mustBe = dict(authRes=True,
                      notAuthRes=True,
                      msg="Page not found")
        actual = dict(authRes=is_hash_not_empty(authRes),
                      notAuthRes=is_hash_not_empty(notAuthRes),
                      msg=notAuthResNotExist["msg"])
        self.unit.assertDictEqual(mustBe, actual, "Not all assertions passed in test_content_hash")

    def test_get_ecosystem_name(self):
        id = 1
        asserts = ["ecosystem_name"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts, setup_vars())

    def test_get_ecosystem_name_new(self):
        data = {"Name": "ecos_" + tools.generate_random_name()}
        res = self.call("NewEcosystem", data, setup_vars())
        id = self.check_get_api("/list/ecosystems", "", [], setup_vars())["count"]
        asserts = ["ecosystem_name"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts, setup_vars())

    def test_get_ecosystem_name_incorrect(self):
        id = 99999
        asserts = ["error"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts, setup_vars())

