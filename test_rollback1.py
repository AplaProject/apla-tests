import unittest
import json
import time
import os

from libs.actions import Actions
from libs.tools import Tools
from libs.db import Db


class TestRollback1(unittest.TestCase):

    def setUp(self):
        global url, prKey, token, waitTx, db
        self.conf = Tools.readConfig("main")
        url = self.conf["url"]
        prKey = self.conf['private_key']
        db = self.conf["db"]
        waitTx = Tools.readConfig("test")["wait_tx_status"]
        lData = Actions.login(url, prKey, 0)
        token = lData["jwtToken"]

    def impApp(self, appName, url, prKey, token):
        path = os.path.join(os.getcwd(), "fixtures", "basic", appName + ".json")
        with open(path, 'r', encoding="utf8") as f:
            file = f.read()
        files = {'input_file': file}
        resp = Actions.call_contract_with_files(url, prKey, "ImportUpload", {},
                                              files, token)
        if ("hash" in resp):
            resImportUpload = Actions.txstatus(url, 30,
                                             resp["hash"], token)
            if int(resImportUpload["blockid"]) > 0:
                founderID = Actions.call_get_api(url + "/ecosystemparam/founder_account/", "", token)['value']
                result = Actions.call_get_api(url + "/list/buffer_data", "", token)
                buferDataList = result['list']
                for item in buferDataList:
                    if item['key'] == "import" and item['member_id'] == founderID:
                        importAppData = json.loads(item['value'])['data']
                        break
                contractName = "Import"
                data = [{"contract": contractName,
                         "params": importAppData[i]} for i in range(len(importAppData))]
                resp = Actions.call_multi_contract(url, prKey, contractName, data, token)
                time.sleep(30)
                if "hashes" in resp:
                    hashes = resp['hashes']
                    result = Actions.txstatus_multi(url, 30, hashes, token)
                    for status in result.values():
                        if int(status["blockid"]) < 1:
                            print("Import is failed")
                            exit(1)
                    print("App '" + appName + "' successfully installed")


    def call(self, name, data):
        resp = Actions.call_contract(url, prKey, name, data, token)
        res = Actions.txstatus(url, waitTx,
                             resp['hash'], token)
        return res

    def create_contract(self, data):
        code, name = Tools.generate_name_and_code("")
        dataC = {}
        if data == "":
            dataC = {"Wallet": '', "ApplicationId": 1,
                     "Value": code,
                     "Conditions": "ContractConditions(`MainCondition`)"}
        else:
            dataC = data
        res = self.call("NewContract", dataC)
        return name, code

    def addNotification(self):
        # create contract, wich added record in notifications table
        body = """
        {
        data {}
        conditions {}
        action {
            DBInsert("notifications", {"recipient->member_id": "-8399130570195839739",
                                        "notification->type": 1,
                                        "notification->header": "Message header",
                                        "notification->body": "Message body"}) 
            }
        }
        """
        code, name = Tools.generate_name_and_code(body)
        data = {"Wallet": '', "ApplicationId": 1,
                "Value": code,
                "Conditions": "ContractConditions(`MainCondition`)"}
        res = self.call("NewContract", data)
        self.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # change permission for notifications table
        dataEdit = {}
        dataEdit["Name"] = "notifications"
        dataEdit["InsertPerm"] = "true"
        dataEdit["UpdatePerm"] = "true"
        dataEdit["ReadPerm"] = "true"
        dataEdit["NewColumnPerm"] = "true"
        res = self.call("EditTable", dataEdit)
        # call contract, wich added record in notification table
        res = self.call(name, "")
        # change permission for notifications table back
        dataEdit = {}
        dataEdit["Name"] = "notifications"
        dataEdit["InsertPerm"] = "ContractAccess(\"Notifications_Single_Send_map\",\"Notifications_Roles_Send_map\")"
        dataEdit["UpdatePerm"] = "ContractConditions(\"MainCondition\")"
        dataEdit["ReadPerm"] = "ContractConditions(\"MainCondition\")"
        dataEdit["NewColumnPerm"] = "ContractConditions(\"MainCondition\")"
        res = self.call("EditTable", dataEdit)

    def getCountTable(self,name):
        return Db.getCountTable(db, name)

    def addBinary(self):
        name = "image_" + Actions.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1}
        resp = Actions.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        res = Actions.txstatus(url, waitTx,
                             resp['hash'], token)
        self.assertGreater(int(res['blockid']), 0, "BlockId is not generated: " + str(res))

    def addUserTable(self):
        # add table
        column = """[{"name":"MyName","type":"varchar", 
                    "index": "1", "conditions":"true"},
                    {"name":"ver_on_null","type":"varchar",
                    "index": "1", "conditions":"true"}]"""
        permission = """{"read": "true",
                        "insert": "true",
                        "update": "true",
                        "new_column": "true"}"""
        tableName = "rolltab_" +  Tools.generate_random_name()
        data = {"Name": tableName,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        return tableName

    def insertToUserTable(self, tableName):
        # create contarct, wich added record in created table
        body = """
        {
        data {}
        conditions {}
        action {
            DBInsert("%s", {MyName: "insert"})
            }
        }
        """ % tableName
        code, name = Tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        # call contarct, wich added record in created table
        res = self.call(name, data)

    def updateUserTable(self, tableName):
        # create contarct, wich updated record in created table
        body = """
        {
        data {}
        conditions {}
        action {
            DBUpdate("%s", 1, {MyName: "update", ver_on_null: "update"})
            }
        }
        """ % tableName
        code, name = Tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        # call contarct, wich added record in created table
        res = self.call(name, data)

    def create_ecosystem(self):
        data = {"Name": "Ecosys" + Tools.generate_random_name()}
        res = self.call("NewEcosystem", data)

    def money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200",
                "Amount": "1000"}
        res = self.call("MoneyTransfer", data)

    def edit_contract(self, contract, code):
        data2 = {"Id": Actions.get_contract_id(url, contract, token),
                 "Value": code,
                 "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        res = self.call("EditContract", data2)

    def activate_contract(self, name):
        data = {"Id": Actions.get_contract_id(url, name, token)}
        res = self.call("ActivateContract", data)

    def deactivate_contract(self, name):
        data = {"Id": Actions.get_contract_id(url, name, token)}
        res = self.call("DeactivateContract", data)

    def new_parameter(self):
        name = "Par_" + Tools.generate_random_name()
        data = {"Name": name,
                "Value": "test",
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        return name

    def edit_parameter(self, name):
        data = {"Id": Actions.get_parameter_id(url, name, token),
                "Value": "test_edited", "Conditions": "true"}
        res = self.call("EditParameter", data)

    def new_menu(self):
        name = "Menu_" + Tools.generate_random_name()
        data = {"Name": name,
                "Value": "Item1",
                "Title": name,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        return name

    def edit_menu(self):
        dataEdit = {"Id": Actions.get_count(url, "menu", token),
                    "Value": "ItemEdited",
                    "Title": "TitleEdited",
                    "Conditions": "true"}
        res = self.call("EditMenu", dataEdit)

    def append_memu(self):
        count = Actions.get_count(url, "menu", token)
        dataEdit = {"Id": Actions.get_count(url, "menu", token),
                    "Value": "AppendedItem"}
        res = self.call("AppendMenu", dataEdit)

    def new_page(self):
        data = {"ApplicationId": 1,
                "Name": "Page_" + Tools.generate_random_name(),
                "Value": "Hello page!",
                "Menu": "default_menu",
                "Conditions": "true"}
        res = self.call("NewPage", data)

    def edit_page(self):
        dataEdit = {"Id": Actions.get_count(url, "pages", token),
                    "Value": "Good by page!",
                    "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("EditPage", dataEdit)

    def append_page(self):
        count = Actions.get_count(url, "pages", token)
        dataEdit = {"Id": Actions.get_count(url, "pages", token),
                    "Value": "Good by!",
                    "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("AppendPage", dataEdit)

    def new_block(self):
        name = "Block_" + Tools.generate_random_name()
        data = {"ApplicationId": 1,
                "Name": name,
                "Value": "Hello page!",
                "Conditions": "true"}
        res = self.call("NewBlock", data)

    def edit_block(self):
        count = Actions.get_count(url, "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!",
                    "Conditions": "true"}
        res = self.call("EditBlock", dataEdit)

    def new_table(self):
        column = """[{"name":"MyName","type":"varchar",
                    "index": "1","conditions":"true"}]"""
        permission = """{"read": "true",
                        "insert": "false",
                        "update" : "true",
                        "new_column": "true"}"""
        data = {"Name": "Tab_" + Tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        return data["Name"]


    def edit_table(self, name):
        dataEdit = {}
        dataEdit["Name"] = name
        dataEdit["InsertPerm"] = "true"
        dataEdit["UpdatePerm"] = "true"
        dataEdit["ReadPerm"] = "true"
        dataEdit["NewColumnPerm"] = "true"
        res = self.call("EditTable", dataEdit)

    def new_column(self, table):
        name = "Col_" + Tools.generate_random_name()
        dataCol = {"TableName": table,
                   "Name": name,
                   "Type": "number",
                   "UpdatePerm": "true",
                   "ReadPerm": "true"}
        res = self.call("NewColumn", dataCol)
        return name

    def edit_column(self, table, column):
        dataEdit = {"TableName": table,
                    "Name": column,
                    "UpdatePerm": "false",
                    "ReadPerm": "false"}
        res = self.call("EditColumn", dataEdit)

    def new_lang(self):
        name = "Lang_" + Tools.generate_random_name()
        data = {"Name": name, "ApplicationId": 1,
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("NewLang", data)
        return name

    def edit_lang(self, id, name):
        dataEdit = {"Id": id,
                    "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("EditLang", dataEdit)

    def new_sign(self):
        name = "Sign_" + Tools.generate_random_name()
        value = "{ \"forsign\" :\"" + name
        value += "\" ,  \"field\" :  \"" + name
        value += "\" ,  \"title\": \"" + name
        value += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value}
        res = self.call("NewSign", data)
        return name

    def edit_sign(self, name):
        count = Actions.get_count(url, "signatures", token)
        valueE = "{ \"forsign\" :\"" + name
        valueE += "\" ,  \"field\" :  \"" + name
        valueE += "\" ,  \"title\": \"" + name
        valueE += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        dataEdit = {"Id": Actions.get_count(url, "signatures", token),
                    "Value": valueE,
                    "Conditions": "true"}
        res = self.call("EditSign", dataEdit)

    def test_rollback1(self):
        # Install apps
        self.impApp("admin", url, prKey, token)
        self.impApp("system_parameters", url, prKey, token)
        print("Start rollback test")
        self.addNotification()
        self.addBinary()
        tableName = self.addUserTable()
        self.insertToUserTable(tableName)
        # Save to file block id for rollback
        rollbackBlockId = Actions.get_max_block_id(url, token)
        file = os.path.join(os.getcwd(), "blockId.txt")
        with open(file, 'w') as f:
            f.write(str(rollbackBlockId))
        # Save to file user table name
        tableNameWithPrefix = "1_" + tableName
        file = os.path.join(os.getcwd(), "userTableName.txt")
        with open(file, 'w') as f:
            f.write(tableNameWithPrefix)
        # Save to file user table state
        dbUserTableInfo = Db.getUserTableState(db, tableNameWithPrefix)
        file = os.path.join(os.getcwd(), "dbUserTableState.json")
        with open(file, 'w') as fconf:
            json.dump(dbUserTableInfo, fconf)
        # Save to file all tables state
        dbInformation = Db.getCountDBObjects(db)
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'w') as fconf:
            json.dump(dbInformation, fconf)
        self.updateUserTable(tableName)
        self.money_transfer()
        contract, code = self.create_contract("")
        self.edit_contract(contract, code)
        self.activate_contract(contract)
        self.deactivate_contract(contract)
        param = self.new_parameter()
        self.edit_parameter(param)
        menu = self.new_menu()
        self.edit_menu()
        self.append_memu()
        self.new_page()
        self.edit_page()
        self.append_page()
        self.new_block()
        self.edit_block()
        table = self.new_table()
        self.edit_table(table)
        column = self.new_column(table)
        self.edit_column(table, column)
        lang = self.new_lang()
        langs = Actions.call_get_api(url + "/list/languages", {}, token)
        self.edit_lang(langs["count"], lang)
        sign = self.new_sign()
        self.edit_sign(sign)
        self.impApp("basic", url, prKey, token)
        time.sleep(20)
