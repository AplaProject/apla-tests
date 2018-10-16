import unittest
import json
import time
import os

from libs import actions, tools, db


class TestRollback1():
    conf = tools.read_config("main")
    url = conf["url"]
    pr_key = conf['private_key']
    db_node = conf["db"]
    l_data = actions.login(url, pr_key, 0)
    token = l_data["jwtToken"]
    wait = tools.read_config("test")["wait_tx_status"]

    def setup_class(self):
        self.unit = unittest.TestCase()

    def imp_app(self, app_name, url, pr_key, token):
        path = os.path.join(os.getcwd(), "fixtures", "basic", app_name + ".json")
        resp = actions.call_contract(url, pr_key, "ImportUpload",
                                     {'input_file': {'Path': path}}, token)
        res_import_upload = actions.tx_status(url, 30, resp, token)
        if int(res_import_upload["blockid"]) > 0:
            founder_id = actions.call_get_api(url + "/ecosystemparam/founder_account/", "", token)['value']
            result = actions.call_get_api(url + "/list/buffer_data", "", token)
            bufer_data_list = result['list']
            for item in bufer_data_list:
                if item['key'] == "import" and item['member_id'] == founder_id:
                    import_app_data = json.loads(item['value'])['data']
                    break
            contract_name = "Import"
            data = [{"contract": contract_name,
                     "params": import_app_data[i]} for i in range(len(import_app_data))]
            resp = actions.call_multi_contract(url, pr_key, contract_name, data, token)
            time.sleep(30)
            if "hashes" in resp:
                hashes = resp['hashes']
                result = actions.tx_status_multi(url, 30, hashes, token)
                for status in result.values():
                    print("status: ", status)
                    if int(status["blockid"]) < 1:
                        print("Import is failed")
                        exit(1)
                print("App '" + app_name + "' successfully installed")


    def call(self, name, data):
        resp = actions.call_contract(self.url, self.pr_key, name,
                                     data, self.token)
        res = actions.tx_status(self.url, self.wait,
                             resp, self.token)
        return res

    def create_contract(self, data):
        code, name = tools.generate_name_and_code("")
        dataC = {}
        if data == "":
            dataC = {"ApplicationId": 1,
                     "Value": code,
                     "Conditions": "ContractConditions(\"MainCondition\")"}
        else:
            dataC = data
        res = self.call("NewContract", dataC)
        return name, code

    def add_notification(self):
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
        code, name = tools.generate_name_and_code(body)
        data = {"Wallet": '', "ApplicationId": 1,
                "Value": code,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # change permission for notifications table
        data_edit = {}
        data_edit["Name"] = "notifications"
        data_edit["InsertPerm"] = "true"
        data_edit["UpdatePerm"] = "true"
        data_edit["ReadPerm"] = "true"
        data_edit["NewColumnPerm"] = "true"
        res = self.call("EditTable", data_edit)
        # call contract, wich added record in notification table
        res = self.call(name, "")
        # change permission for notifications table back
        data_edit = {}
        data_edit["Name"] = "notifications"
        data_edit["InsertPerm"] = "ContractAccess(\"Notifications_Single_Send_map\",\"Notifications_Roles_Send_map\")"
        data_edit["UpdatePerm"] = "ContractConditions(\"MainCondition\")"
        data_edit["ReadPerm"] = "ContractConditions(\"MainCondition\")"
        data_edit["NewColumnPerm"] = "ContractConditions(\"MainCondition\")"
        res = self.call("EditTable", data_edit)

    def add_binary(self):
        name = "image_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1, 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key,
                                                "UploadBinary", data, self.token)
        res = actions.tx_status(self.url, self.wait,
                             resp, self.token)
        self.unit.assertGreater(int(res['blockid']), 0, "BlockId is not generated: " + str(res))

    def add_user_table(self):
        # add table
        column = """[{"name":"MyName","type":"varchar", 
                    "index": "1", "conditions":"true"},
                    {"name":"ver_on_null","type":"varchar",
                    "index": "1", "conditions":"true"}]"""
        permission = """{"read": "true",
                        "insert": "true",
                        "update": "true",
                        "new_column": "true"}"""
        table_name = "rolltab_" +  tools.generate_random_name()
        data = {"Name": table_name,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        return table_name

    def insert_to_user_table(self, table_name):
        # create contarct, wich added record in created table
        body = """
        {
        data {}
        conditions {}
        action {
            DBInsert("%s", {MyName: "insert"})
            }
        }
        """ % table_name
        code, name = tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        # call contarct, wich added record in created table
        data = {}
        res = self.call(name, data)

    def update_user_table(self, table_name):
        # create contarct, wich updated record in created table
        body = """
        {
        data {}
        conditions {}
        action {
            DBUpdate("%s", 1, {MyName: "update", ver_on_null: "update"})
            }
        }
        """ % table_name
        code, name = tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        # call contarct, wich added record in created table
        data = {}
        res = self.call(name, data)

    def create_ecosystem(self):
        data = {"Name": "Ecosys" + tools.generate_random_name()}
        res = self.call("NewEcosystem", data)

    def tokens_send(self):
        data = {"Recipient_Account": "4544233900443112470",
                "Amount": "1000"}
        res = self.call("TokensSend", data)

    def edit_contract(self, contract, code):
        data2 = {"Id": actions.get_contract_id(self.url, contract,
                                               self.token),
                 "Value": code.replace('action {    } ', 'action { var a map   } '),
                 "Conditions": "true"}
        res = self.call("EditContract", data2)

    def activate_contract(self, name):
        data = {"Id": actions.get_contract_id(self.url, name, self.token)}
        res = self.call("ActivateContract", data)

    def deactivate_contract(self, name):
        data = {"Id": actions.get_contract_id(self.url, name, self.token)}
        res = self.call("DeactivateContract", data)

    def new_parameter(self):
        name = "Par_" + tools.generate_random_name()
        data = {"Name": name,
                "Value": "test",
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        return name

    def edit_parameter(self, name):
        data = {"Id": actions.get_parameter_id(self.url, name, self.token),
                "Value": "test_edited", "Conditions": "true"}
        res = self.call("EditParameter", data)

    def new_menu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name,
                "Value": "Item1",
                "Title": name,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        return name

    def edit_menu(self):
        data_edit = {"Id": actions.get_count(self.url, "menu", self.token),
                    "Value": "ItemEdited",
                    "Title": "TitleEdited",
                    "Conditions": "true"}
        res = self.call("EditMenu", data_edit)

    def append_memu(self):
        count = actions.get_count(self.url, "menu", self.token)
        data_edit = {"Id": actions.get_count(self.url, "menu", self.token),
                    "Value": "AppendedItem"}
        res = self.call("AppendMenu", data_edit)

    def new_page(self):
        data = {"ApplicationId": 1,
                "Name": "Page_" + tools.generate_random_name(),
                "Value": "Hello page!",
                "Menu": "default_menu",
                "Conditions": "true"}
        res = self.call("NewPage", data)

    def edit_page(self):
        data_edit = {"Id": actions.get_count(self.url, "pages", self.token),
                    "Value": "Good by page!",
                    "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("EditPage", data_edit)

    def append_page(self):
        count = actions.get_count(self.url, "pages", self.token)
        data_edit = {"Id": actions.get_count(self.url, "pages", self.token),
                    "Value": "Good by!",}
        res = self.call("AppendPage", data_edit)

    def new_block(self):
        name = "Block_" + tools.generate_random_name()
        data = {"ApplicationId": 1,
                "Name": name,
                "Value": "Hello page!",
                "Conditions": "true"}
        res = self.call("NewBlock", data)

    def edit_block(self):
        count = actions.get_count(self.url, "blocks", self.token)
        data_edit = {"Id": count, "Value": "Good by!",
                    "Conditions": "true"}
        res = self.call("EditBlock", data_edit)

    def new_table(self):
        column = """[{"name":"MyName","type":"varchar",
                    "index": "1","conditions":"true"}]"""
        permission = """{"read": "true",
                        "insert": "false",
                        "update" : "true",
                        "new_column": "true"}"""
        data = {"Name": "tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        return data["Name"]


    def edit_table(self, name):
        data_edit = {}
        data_edit["Name"] = name
        data_edit["InsertPerm"] = "true"
        data_edit["UpdatePerm"] = "true"
        data_edit["ReadPerm"] = "true"
        data_edit["NewColumnPerm"] = "true"
        res = self.call("EditTable", data_edit)

    def new_column(self, table):
        name = 'Col_' + tools.generate_random_name()
        data_col = {"TableName": table,
                   "Name": name,
                   "Type": "number",
                   "UpdatePerm": "true",
                   "ReadPerm": "true"}
        res = self.call("NewColumn", data_col)
        return name

    def edit_column(self, table, column):
        data_edit = {"TableName": table,
                    "Name": column,
                    "UpdatePerm": "false",
                    "ReadPerm": "false"}
        res = self.call("EditColumn", data_edit)

    def new_lang(self):
        name = "Lang_" + tools.generate_random_name()
        data = {"Name": name,
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("NewLang", data)
        return name

    def edit_lang(self, id, name):
        data_edit = {"Id": id,
                    "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("EditLang", data_edit)

    def new_sign(self):
        name = "Sign_" + tools.generate_random_name()
        value = "{ \"forsign\" :\"" + name
        value += "\" ,  \"field\" :  \"" + name
        value += "\" ,  \"title\": \"" + name
        value += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value}
        res = self.call("NewSign", data)
        return name

    def edit_sign(self, name):
        count = actions.get_count(self.url, "signatures", self.token)
        value_e = "{ \"forsign\" :\"" + name
        value_e += "\" ,  \"field\" :  \"" + name
        value_e += "\" ,  \"title\": \"" + name
        value_e += "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data_edit = {"Id": actions.get_count(self.url, "signatures",
                                            self.token),
                    "Value": value_e,
                    "Conditions": "true"}
        res = self.call("EditSign", data_edit)

    def test_rollback1(self):
        print("Start rollback test")
        # Install apps
        self.imp_app("system", self.url, self.pr_key, self.token)
        self.imp_app("basic", self.url, self.pr_key, self.token)
        print("1")
        table_name = self.add_user_table()
        print("2")
        self.insert_to_user_table(table_name)
        # Save to file block id for rollback
        rollback_block_id = actions.get_max_block_id(self.url, self.token)
        file = os.path.join(os.getcwd(), "blockId.txt")
        with open(file, 'w') as f:
            f.write(str(rollback_block_id))
        # Save to file user table name
        table_name_with_prefix = "1_" + table_name
        file = os.path.join(os.getcwd(), "userTableName.txt")
        with open(file, 'w') as f:
            f.write(table_name_with_prefix)
        # Save to file user table state
        db_user_table_info = db.get_user_table_state(self.db_node, table_name_with_prefix)
        file = os.path.join(os.getcwd(), "dbUserTableState.json")
        with open(file, 'w') as fconf:
            json.dump(db_user_table_info, fconf)
        # Save to file all tables state
        db_information = db.get_count_DB_objects(self.url, self.token)
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'w') as fconf:
            json.dump(db_information, fconf)
        self.insert_to_user_table(table_name)
        self.update_user_table(table_name)
        self.add_notification()
        self.add_binary()
        self.tokens_send()
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
        langs = actions.call_get_api(self.url + "/list/languages", {}, self.token)
        self.edit_lang(langs["count"], lang)
        #sign = self.new_sign()
        #self.edit_sign(sign)
        self.imp_app("conditions", self.url, self.pr_key, self.token)
        time.sleep(20)
