import unittest
import utils
import config
import requests
import json


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.readMainConfig()
        self.data = utils.login(self.config["url"], self.config['private_key'])

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        url = self.config["url"]
        pause = self.config["time_wait_tx_in_block"]
        status = utils.txstatus(url, pause, result['hash'], jwtToken)
        self.assertNotIn(json.dumps(status), 'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def call_get_api(self, endPoint, data):
        url = self.config['url'] + endPoint
        token = self.data["jwtToken"]
        resp = requests.get(url, data=data,  headers={"Authorization": token})
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def call_post_api(self, endPoint, data):
        url = self.config['url'] + endPoint
        token = self.data["jwtToken"]
        resp = requests.post(url, data=data,  headers={"Authorization": token})
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def check_get_api(self, endPoint, data, keys):
        result = self.call_get_api(endPoint, data)
        for key in keys:
            self.assertIn(key, result)

    def check_post_api(self, endPoint, data, keys):
        result = self.call_post_api(endPoint, data)
        for key in keys:
            self.assertIn(key, result)

    def call(self, name, data):
        url = self.config["url"]
        prKey = self.config['private_key']
        token = self.data["jwtToken"]
        resp = utils.call_contract(url, prKey, name, data, token)
        self.assertTxInBlock(resp, self.data["jwtToken"])
        return resp

    def get_count(self, type):
        res = self.call_get_api("/list/" + type, "")
        return res["count"]

    def get_contract_id(self, name):
        res = self.call_get_api("/contract/" + name, "")
        return res["tableid"]

    def get_parameter_id(self, name):
        res = self.call_get_api("/ecosystemparam/" + name, "")
        return res["id"]

    def get_parameter_value(self, name):
        res = self.call_get_api("/ecosystemparam/" + name, "")
        return res["value"]

    def get_content(self, type, name, lang):
        if(lang != ""):
            data = {"lang": lang}
        else:
            data = ""
        res = self.call_post_api("/content/" + type + "/" + name, data)
        return res

    def test_balance(self):
        asserts = ["amount", "money"]
        self.check_get_api('/balance/' + self.data['address'], "", asserts)

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
        asserts = ["name"]
        data = {}
        self.check_get_api("/table/contracts", data, asserts)

    def test_get_table_data(self):
        asserts = ["list"]
        data = {}
        self.check_get_api("/list/menu", data, asserts)

    def test_get_table_data_row(self):
        asserts = ["value"]
        data = {}
        self.check_get_api("/row/contracts/2", data, asserts)

    def test_get_contract_information(self):
        asserts = ["name"]
        data = {}
        self.check_get_api("/contract/MainCondition", data, asserts)

    def test_create_ecosystem(self):
        name = "Ecosys" + utils.generate_random_name()
        data = {"name": name}
        res = self.call("NewEcosystem", data)

    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "1000"}
        self.call("MoneyTransfer", data)

    def test_money_transfer_with_comment(self):
        wallet = "0005-2070-2000-0006-0200"
        data = {"Recipient": wallet, "Amount": "1000", "Comment": "Test"}
        self.call("MoneyTransfer", data)

    def test_new_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)

    def test_activate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        id = self.get_contract_id(name)
        data2 = {"Id": id}
        self.call("ActivateContract", data2)

    def test_deactivate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        id = self.get_contract_id(name)
        data2 = {"Id": id}
        self.call("ActivateContract", data2)
        self.call("DeactivateContract", data2)

    def test_edit_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "Conditions": "true"}
        self.call("NewContract", data)
        data2 = {}
        data2["Id"] = self.get_contract_id(name)
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = newWallet
        self.call("EditContract", data2)

    def test_new_parameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        self.call("NewParameter", data)

    def test_edit_parameter(self):
        newVal = "test_edited"
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        self.call("NewParameter", data)
        id = self.get_parameter_id(name)
        data2 = {"Id": id, "Value": newVal, "Conditions": "true"}
        self.call("EditParameter", data2)
        value = self.get_parameter_value(name)
        self.assertEqual(value, newVal, "Parameter didn't change")

    def test_new_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        self.assertEqual(self.get_content("menu", name, ""), content)

    def test_edit_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        count = self.get_count("menu")
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        self.call("EditMenu", dataEdit)
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        self.assertEqual(self.get_content("menu", name, ""), content)

    def test_append_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        count = self.get_count("menu")
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        self.call("AppendMenu", dataEdit)
        content = {'tree': [{'tag': 'text', 'text': 'Item1\r\nAppendedItem'}]}
        self.assertEqual(self.get_content("menu", name, ""), content)

    def test_new_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = self.get_content("page", name, "")
        self.assertEqual(cont, content)

    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        dataEdit = {}
        dataEdit["Id"] = self.get_count("pages")
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        self.call("EditPage", dataEdit)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Good by page!'}]
        self.assertEqual(self.get_content("page", name, ""), content)

    def test_append_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        count = self.get_count("pages")
        dataEdit = {}
        dataEdit["Id"] = self.get_count("pages")
        dataEdit["Value"] = "Good by!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        self.call("AppendPage", dataEdit)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        self.assertEqual(self.get_content("page", name, ""), content)

    def test_new_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "Conditions": "true"}
        self.call("NewBlock", data)

    def test_edit_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "Conditions": "true"}
        self.call("NewBlock", data)
        count = self.get_count("blocks")
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        self.call("EditBlock", dataEdit)

    def test_new_table(self):
        data = {}
        data["Name"] = "Tab_" + utils.generate_random_name()
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1 = "{\"insert\": \"false\","
        per2 = " \"update\" : \"true\","
        per3 = " \"new_column\": \"true\"}"
        data["Permissions"] = per1 + per2 + per3
        self.call("NewTable", data)

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
        self.call("NewTable", data)
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        data["Columns"] = col1 + col2
        per1E = "{\"insert\": \"true\","
        per2E = " \"update\" : \"true\","
        per3E = " \"new_column\": \"true\"}"
        dataEdit["Permissions"] = per1E + per2E + per3E
        self.call("EditTable", dataEdit)

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
        self.call("NewTable", data)
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = nameTab
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        self.call("NewColumn", dataCol)

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
        self.call("NewTable", data)
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = nameTab
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        self.call("NewColumn", dataCol)
        dataEdit = {"TableName": nameTab, "Name": name, "Permissions": "false"}
        self.call("EditColumn", dataEdit)

    def test_new_lang(self):
        data = {}
        data["Name"] = "Lang_" + utils.generate_random_name()
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        self.call("NewLang", data)

    def test_edit_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        self.call("NewLang", data)
        dataEdit = {}
        dataEdit["Name"] = name
        dataEdit["Trans"] = "{\"en\": \"true\", \"ru\" : \"true\"}"
        self.call("EditLang", dataEdit)

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
        self.call("NewSign", data)

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
        self.call("NewSign", data)
        count = self.get_count("signatures")
        dataEdit = {}
        dataEdit["Id"] = count
        valueE = "{ \"forsign\" :\"" + name
        valueE += "\" ,  \"field\" :  \"" + name
        valueE += "\" ,  \"title\": \"" + name
        valueE += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        dataEdit["Value"] = valueE
        dataEdit["Conditions"] = "true"
        self.call("EditSign", dataEdit)

    def test_content_lang(self):
        nameLang = "Lang_" + utils.generate_random_name()
        data = {}
        data["Name"] = nameLang
        data["Trans"] = "{\"en\": \"fist\", \"ru\" : \"second\"}"
        self.call("NewLang", data)
        namePage = "Page_" + utils.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang + ")"
        dataPage = {}
        dataPage["Name"] = namePage
        dataPage["Value"] = valuePage
        dataPage["Conditions"] = "true"
        dataPage["Menu"] = "default_menu"
        self.call("NewPage", dataPage)
        content = {}
        content["menu"] = 'default_menu'
        menutree = {}
        menutree["tag"] = 'menuitem'
        menutree["attr"] = {'page': 'Default Ecosystem Menu', 'title': 'main'}
        content["menutree"] = []
        content["tree"] = [{'tag': 'text', 'text': 'Hello, fist'}]
        contentRu = {}
        contentRu["menu"] = 'default_menu'
        contentRu["menutree"] = []
        contentRu["tree"] = [{'tag': 'text', 'text': 'Hello, second'}]
        self.assertEqual(self.get_content("page", namePage, "ru"), contentRu)
        self.assertEqual(self.get_content("page", namePage, ""), content)

    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde": "true"}
        self.check_get_api("/table/contracts", data, asserts)

    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        #self.check_post_api("/vde/create", data, asserts)

if __name__ == '__main__':
    unittest.main()
