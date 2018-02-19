import unittest
import utils
import config
import json
import time
import funcs
import os


class Rollback1TestCase(unittest.TestCase):
    
    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        
    def create_contract(self, data):
        code,name = utils.generate_name_and_code("")
        dataC = {}
        if data == "":
            dataC["Wallet"] = ''
            dataC["Value"] = code
            dataC["Conditions"] = "ContractConditions(`MainCondition`)"
        else:
            dataC = data
        self.call("NewContract", dataC)
        return name, code
        
    def create_ecosystem(self):
        name = "Ecosys" + utils.generate_random_name()
        data = {"name": name}
        self.call("NewEcosystem", data)
        
    def money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "1000"}
        self.call("MoneyTransfer", data)
        
    def edit_contract(self,contract, code):
        data2 = {}
        print(url)
        print(contract)
        print(token)
        data2["Id"] = funcs.get_contract_id(url, contract, token)
        data2["Value"] = code
        data2["Conditions"] = "true"
        data2["WalletId"] = "0005-2070-2000-0006-0200"
        self.call("EditContract", data2)
        
    def activate_contract(self, name):
        id = funcs.get_contract_id(url, name, token)
        data = {"Id": id}
        self.call("ActivateContract", data)
        
    def deactivate_contract(self, name):
        id = funcs.get_contract_id(url, name, token)
        data = {"Id": id}
        self.call("DeactivateContract", data)
        
    def new_parameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        self.call("NewParameter", data)
        return name
    
    def edit_parameter(self, name):
        id = funcs.get_parameter_id(url, name, token)
        data = {"Id": id, "Value": "test_edited", "Conditions": "true"}
        self.call("EditParameter", data)
        
    def new_menu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        self.call("NewMenu", data)
        return name
    
    def edit_menu(self):
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        self.call("EditMenu", dataEdit)
        
    def append_memu(self):
        count = funcs.get_count(url, "menu", token)
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        self.call("AppendMenu", dataEdit)
        
    def new_page(self):
        name = "Page_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "Hello page!"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        self.call("NewPage", data)
        
    def edit_page(self):
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by page!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        self.call("EditPage", dataEdit)
        
    def append_page(self):
        count = funcs.get_count(url, "pages", token)
        dataEdit = {}
        dataEdit["Id"] = funcs.get_count(url, "pages", token)
        dataEdit["Value"] = "Good by!"
        dataEdit["Conditions"] = "true"
        dataEdit["Menu"] = "default_menu"
        self.call("AppendPage", dataEdit)
        
    def new_block(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "Conditions": "true"}
        self.call("NewBlock", data)
        
    def edit_block(self):
        count = funcs.get_count(url, "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        self.call("EditBlock", dataEdit)
        
    def new_table(self):
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
        return data["Name"]

    def edit_table(self, name):
        dataEdit = {}
        dataEdit["Name"] = name
        col1 = "[{\"name\":\"MyName\",\"type\":\"varchar\","
        col2 = "\"index\": \"1\",  \"conditions\":\"true\"}]"
        dataEdit["Columns"] = col1 + col2
        per1E = "{\"insert\": \"true\","
        per2E = " \"update\" : \"true\","
        per3E = " \"new_column\": \"true\"}"
        dataEdit["Permissions"] = per1E + per2E + per3E
        self.call("EditTable", dataEdit)

    def new_column(self, table):
        name = "Col_" + utils.generate_random_name()
        dataCol = {}
        dataCol["TableName"] = table
        dataCol["Name"] = name
        dataCol["Type"] = "number"
        dataCol["Index"] = "0"
        dataCol["Permissions"] = "true"
        self.call("NewColumn", dataCol)
        return name

    def edit_column(self, table, column):
        dataEdit = {"TableName": table, "Name": column, "Permissions": "false"}
        self.call("EditColumn", dataEdit)

    def new_lang(self):
        name = "Lang_" + utils.generate_random_name()
        data = {}
        data["Name"] = name
        data["Trans"] = "{\"en\": \"false\", \"ru\" : \"true\"}"
        self.call("NewLang", data)
        return name

    def edit_lang(self, name):
        dataEdit = {}
        dataEdit["Name"] = name
        dataEdit["Trans"] = "{\"en\": \"true\", \"ru\" : \"true\"}"
        self.call("EditLang", dataEdit)

    def new_sign(self):
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
        return name

    def edit_sign(self, name):
        count = funcs.get_count(url, "signatures", token)
        dataEdit = {}
        dataEdit["Id"] = count
        valueE = "{ \"forsign\" :\"" + name
        valueE += "\" ,  \"field\" :  \"" + name
        valueE += "\" ,  \"title\": \"" + name
        valueE += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        dataEdit["Value"] = valueE
        dataEdit["Conditions"] = "true"
        self.call("EditSign", dataEdit)
        
    def test_rollback1(self):
        global url, prKey, token
        self.conf = config.readMainConfig()
        url = self.conf["url"]
        prKey = self.conf['private_key']
        host = self.conf["dbHost"]
        db = self.conf["dbName"]
        login = self.conf["login"]
        pas = self.conf["pass"]
        dbInformation = utils.getCountDBObjects(host, db, login, pas)
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'w') as fconf:
            json.dump(dbInformation, fconf)
        lData = utils.login(url, prKey)
        token = lData["jwtToken"]
        self.create_ecosystem()
        self.money_transfer()
        contract,code = self.create_contract("")
        time.sleep(2)
        self.edit_contract(contract,code)
        time.sleep(2)
        self.activate_contract(contract)
        time.sleep(2)
        self.deactivate_contract(contract)
        time.sleep(2)
        param = self.new_parameter()
        time.sleep(2)
        self.edit_parameter(param)
        time.sleep(2)
        menu = self.new_menu()
        time.sleep(2)
        self.edit_menu()
        time.sleep(2)
        self.append_memu()
        time.sleep(2)
        self.new_page()
        time.sleep(2)
        self.edit_page()
        time.sleep(2)
        self.append_page()
        time.sleep(2)
        self.new_block()
        time.sleep(2)
        self.edit_block()
        time.sleep(2)
        table = self.new_table()
        time.sleep(2)
        self.edit_table(table)
        time.sleep(2)
        column = self.new_column(table)
        time.sleep(2)
        self.edit_column(table, column)
        time.sleep(2)
        lang = self.new_lang()
        time.sleep(2)
        self.edit_lang(lang)
        time.sleep(2)
        sign = self.new_sign()
        time.sleep(2)
        self.edit_sign(sign)
        time.sleep(20)
        
if __name__ == "__main__":
    unittest.main()
        