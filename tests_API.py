import unittest
import utils
import config
import requests
import json

class ApiTestCase(unittest.TestCase):
    config = {}
    def setUp(self):
        self.config = config.readMainConfig()
        self.data = utils.login(self.config["url"], self.config['private_key']) 
        
    def assertTxInBlock(self, result, jvtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(self.config["url"],self.config["time_wait_tx_in_block"], result['hash'], jvtToken)
        self.assertNotIn(json.dumps(status),'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def call_get_api(self, endPoint, data):
        resp = requests.get(self.config['url']+ endPoint, data=data,  headers={"Authorization": self.data["jvtToken"]})
        self.assertEqual(resp.status_code, 200)
        return resp.json()
    
    def call_post_api(self, endPoint, data):
        resp = requests.post(self.config['url']+ endPoint, data=data,  headers={"Authorization": self.data["jvtToken"]})
        self.assertEqual(resp.status_code, 200)
        return resp.json()
            
    def check_get_api(self, endPoint, data, asserts):
        result = self.call_get_api(endPoint, data)
        for asert in asserts:
            self.assertIn(asert, result)
            
    def check_post_api(self, endPoint, data, asserts):
        result = self.call_post_api(endPoint, data)
        for asert in asserts:
            self.assertIn(asert, result)
            
    def call(self, name, data):
        resp = utils.call_contract(self.config["url"], self.config['private_key'], name, data, self.data["jvtToken"])
        self.assertTxInBlock(resp, self.data["jvtToken"])
        return resp
        
    def get_count(self, type):
        res = self.call_get_api("/list/" + type, "")
        return res["count"]
    
    def get_contract_id(self, name):
        res = self.call_get_api("/contract/" + name, "")
        return res["tableid"]
    
    def get_parameter_id(self,name):
        res = self.call_get_api("/ecosystemparam/"+name, "")
        return res["id"]
    
    def get_parameter_value(self,name):
        res = self.call_get_api("/ecosystemparam/"+name, "")
        return res["value"]
            
    def get_content(self, type, name, lang):
        if(lang != ""):        
            data = {"lang":lang}
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
        data = {'ecosystem': 1, 'names':"name"} 
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
        data = {"Recipient":"0005-2070-2000-0006-0200","Amount":"1000"}
        self.call("MoneyTransfer", data)
        
    def test_money_transfer_with_comment(self):
        data = {"Recipient":"0005-2070-2000-0006-0200","Amount":"1000","Comment":"Test"}
        self.call("MoneyTransfer", data)
        
    def test_new_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value":code,"Conditions":"true"}
        self.call("NewContract", data)
        
    def test_activate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value":code,"Conditions":"true"}
        self.call("NewContract", data)
        id = self.get_contract_id(name)
        data2 = {"Id":id}
        self.call("ActivateContract", data2)
        
    def test_deactivate_contract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value":code,"Conditions":"true"}
        self.call("NewContract", data)
        id = self.get_contract_id(name)
        data2 = {"Id":id}
        self.call("ActivateContract", data2)
        self.call("DeactivateContract", data2)
        
    def test_edit_contract(self):
        newWallet = "0005-2070-2000-0006-0200"
        code, name = utils.generate_name_and_code("")
        data = {"Value":code,"Conditions":"true"}
        self.call("NewContract", data)
        id = self.get_contract_id(name)
        data2 = {"Id":id, "Value": code, "Conditions": "ContractConditions(`MainCondition`)", "WalletId" : newWallet}
        self.call("EditContract", data2)
      #  info = self.call_get_api("/contract/" + name, "")
      #  self.assertEqual(info["address"], newWallet, "Wallet didn't change")
        
    def test_new_parameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value":"test","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewParameter", data)
        
    def test_edit_parameter(self):
        newVal = "test_edited" 
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value":"test","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewParameter", data)
        id = self.get_parameter_id(name)
        data2 = {"Id": id, "Value":newVal,"Conditions":"ContractConditions(`MainCondition`)"}
        self.call("EditParameter", data2)
        value = self.get_parameter_value(name)
        self.assertEqual(value, newVal, "Parameter didn't change")
        
    def test_new_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Item1","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewMenu", data)   
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        self.assertEqual(self.get_content("menu", name, ""), content)
        
    def test_edit_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Item1","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewMenu", data)
        count = self.get_count("menu")   
        dataEdit = {"Id": count, "Value":"ItemEdited","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("EditMenu", dataEdit)
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        self.assertEqual(self.get_content("menu", name, ""), content)
        
    def test_append_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Item1","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewMenu", data)
        count = self.get_count("menu")   
        dataEdit = {"Id": count, "Value":"AppendedItem","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("AppendMenu", dataEdit)
        content = {'tree': [{'tag': 'text', 'text': 'Item1\r\nAppendedItem'}]}
        self.assertEqual(self.get_content("menu", name, ""), content)
    
    def test_new_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Hello page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("NewPage", data)   
        content = {'menu': 'default_menu', 'menutree': [{'tag': 'menuitem', 'attr': {'page': 'Default Ecosystem Menu', 'title': 'main'}}], 'tree': [{'tag': 'text', 'text': 'Hello page!'}]}
        self.assertEqual(self.get_content("page", name, ""), content) 
        
    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Hello page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("NewPage", data)
        count = self.get_count("pages")   
        dataEdit = {"Id": count, "Value":"Good by page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("EditPage", dataEdit)   
        content = {'menu': 'default_menu', 'menutree': [{'tag': 'menuitem', 'attr': {'page': 'Default Ecosystem Menu', 'title': 'main'}}], 'tree': [{'tag': 'text', 'text': 'Good by page!'}]}
        self.assertEqual(self.get_content("page", name, ""), content)   
        
    def test_edit_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Hello page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("NewPage", data)
        count = self.get_count("pages")   
        dataEdit = {"Id": count, "Value":"Good by page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("EditPage", dataEdit)   
        content = {'menu': 'default_menu', 'menutree': [{'tag': 'menuitem', 'attr': {'page': 'Default Ecosystem Menu', 'title': 'main'}}], 'tree': [{'tag': 'text', 'text': 'Good by page!'}]}
        self.assertEqual(self.get_content("page", name, ""), content)   
        
    def test_append_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Hello page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("NewPage", data)
        count = self.get_count("pages")   
        dataEdit = {"Id": count, "Value":"Good by page!","Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("AppendPage", dataEdit)   
        content = {'menu': 'default_menu', 'menutree': [{'tag': 'menuitem', 'attr': {'page': 'Default Ecosystem Menu', 'title': 'main'}}], 'tree': [{'tag': 'text', 'text': 'Hello page!\r\nGood by page!'}]}
        self.assertEqual(self.get_content("page", name, ""), content)   
        
    def test_new_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Hello page!","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewBlock", data)
    
    def test_edit_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value":"Hello page!","Conditions":"ContractConditions(`MainCondition`)"}
        self.call("NewBlock", data)
        count = self.get_count("blocks")
        dataEdit = {"Id": count, "Value":"Good by bock!","Conditions":"ContractConditions(`MainCondition`)"}     
        self.call("EditBlock", dataEdit)
        
    def test_new_table(self):
        name = "Tab_" + utils.generate_random_name()
        data = {"Name": name, "Columns":"[{\"name\":\"MyName\",\"type\":\"varchar\", \"index\": \"1\",  \"conditions\":\"true\"}, {\"name\":\"Amount\", \"type\":\"number\",\"index\": \"0\", \"conditions\":\"true\"}]","Permissions":"{\"insert\": \"false\", \"update\" : \"true\", \"new_column\": \"true\"}"}
        self.call("NewTable", data) 
        
    def test_edit_table(self):
        name = "Tab_" + utils.generate_random_name()
        data = {"Name": name, "Columns":"[{\"name\":\"MyName\",\"type\":\"varchar\", \"index\": \"1\",  \"conditions\":\"true\"}, {\"name\":\"Amount\", \"type\":\"number\",\"index\": \"0\", \"conditions\":\"true\"}]","Permissions":"{\"insert\": \"false\", \"update\" : \"true\", \"new_column\": \"true\"}"}
        self.call("NewTable", data) 
        dataEdit = {"Name": name, "Permissions":"{\"insert\": \"true\", \"update\" : \"true\", \"new_column\": \"true\"}"}
        self.call("EditTable", dataEdit) 
        
    def test_new_column(self):
        nameTab = "Tab_" + utils.generate_random_name()
        data = {"Name": nameTab, "Columns":"[{\"name\":\"MyName\",\"type\":\"varchar\", \"index\": \"1\",  \"conditions\":\"true\"}, {\"name\":\"Amount\", \"type\":\"number\",\"index\": \"0\", \"conditions\":\"true\"}]","Permissions":"{\"insert\": \"false\", \"update\" : \"true\", \"new_column\": \"true\"}"}
        self.call("NewTable", data) 
        name = "Col_" + utils.generate_random_name()
        dataCol = {"TableName": nameTab, "Name": name, "Type": "number", "Index": "0", "Permissions":"true"}
        self.call("NewColumn", dataCol) 
        
    def test_edit_column(self):
        nameTab = "Tab_" + utils.generate_random_name()
        data = {"Name": nameTab, "Columns":"[{\"name\":\"MyName\",\"type\":\"varchar\", \"index\": \"1\",  \"conditions\":\"true\"}, {\"name\":\"Amount\", \"type\":\"number\",\"index\": \"0\", \"conditions\":\"true\"}]","Permissions":"{\"insert\": \"false\", \"update\" : \"true\", \"new_column\": \"true\"}"}
        self.call("NewTable", data) 
        name = "Col_" + utils.generate_random_name()
        dataCol = {"TableName": nameTab, "Name": name, "Type": "number", "Index": "0", "Permissions":"true"}
        self.call("NewColumn", dataCol) 
        dataEdit = {"TableName": nameTab, "Name": name, "Permissions":"false"}
        self.call("EditColumn", dataEdit) 
    
    def test_new_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {"Name": name, "Trans":"{\"en\": \"false\", \"ru\" : \"true\"}"}
        self.call("NewLang", data)
        
    def test_edit_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {"Name": name, "Trans":"{\"en\": \"false\", \"ru\" : \"true\"}"}
        self.call("NewLang", data)
        dataEdit = {"Name": name, "Trans":"{\"en\": \"true\", \"ru\" : \"true\"}"}
        self.call("EditLang", dataEdit)
        
    def test_new_sign(self):
        name = "Sign_" + utils.generate_random_name()
        data = {"Name": name, "Value":"{ \"forsign\" :\"" + name + "\"  ,  \"field\" :  \"" + name + "\" ,  \"title\": \"" + name + "\", \"params\":[  { \"name\": \"test\", \"text\" : \"test\"}]}", "Conditions":"true"}
        self.call("NewSign", data)
        
    def test_edit_sign(self):
        name = "Sign_" + utils.generate_random_name()
        data = {"Name": name, "Value":"{ \"forsign\" :\"" + name + "\"  ,  \"field\" :  \"" + name + "\" ,  \"title\": \"" + name + "\", \"params\":[  { \"name\": \"test\", \"text\" : \"test\"}]}", "Conditions":"true"}
        self.call("NewSign", data)
        count = self.get_count("signatures")
        dataEdit = {"Id": count, "Value":"{ \"forsign\" :\"" + name + "\"  ,  \"field\" :  \"" + name + "\" ,  \"title\": \"" + name + "\", \"params\":[  { \"name\": \"test1\", \"text\" : \"test1\"}]}", "Conditions":"true"}
        self.call("EditSign", dataEdit)
        
    def test_content_lang(self):
        nameLang = "Lang_" + utils.generate_random_name()
        data = {"Name": nameLang, "Trans":"{\"en\": \"fist\", \"ru\" : \"second\"}"}
        self.call("NewLang", data)
        namePage = "Page_" + utils.generate_random_name()
        valuePage = "Hello, LangRes(" + nameLang +")"
        data = {"Name": namePage, "Value":valuePage,"Conditions":"ContractConditions(`MainCondition`)", "Menu":"default_menu"}
        self.call("NewPage", data)   
        content = {'menu': 'default_menu', 'menutree': [{'tag': 'menuitem', 'attr': {'page': 'Default Ecosystem Menu', 'title': 'main'}}], 'tree': [{'tag': 'text', 'text': 'Hello, fist'}]}
        contentRu = {'menu': 'default_menu', 'menutree': [{'tag': 'menuitem', 'attr': {'page': 'Default Ecosystem Menu', 'title': 'main'}}], 'tree': [{'tag': 'text', 'text': 'Hello, second'}]}
        self.assertEqual(self.get_content("page", namePage, "ru"), contentRu) 
        self.assertEqual(self.get_content("page", namePage, ""), content) 
        
    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde":"true"}
        self.check_get_api("/table/contracts", data, asserts)
        
    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        self.check_post_api("/vde/create", data, asserts)
        
        
        
if __name__ == '__main__':
    unittest.main()
    #utils.install("PRIVATE_NET", "ERROR", "localhost", "5432", "aplafront", "postgres", "postgres", "1", "")      
        