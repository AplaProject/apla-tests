import unittest
import json
import time
import pytest

from libs import actions, db, tools


class TestSimvolio():
    contracts = tools.read_fixtures("simvolio")
    wait = tools.read_config("test")["wait_tx_status"]
    config = tools.read_config("nodes")
    unit = unittest.TestCase()

    def setup(self):
        print("setup class")
        self.url = self.config[1]["url"]
        self.pr_key = self.config[0]['private_key']
        self.db1 = self.config[0]['db']
        data = actions.login(self.url, self.pr_key, 0)
        self.token = data["jwtToken"]

    def assert_tx_in_block(self, result, jwt_token):
        status = actions.tx_status(self.url, self.wait, result, jwt_token)
        print(status)
        self.unit.assertNotIn(json.dumps(status), 'errmsg')
        self.unit.assertGreater(status['blockid'], 0)

    def generate_name_and_code(self, sourseCode):
        name = tools.generate_random_name()
        code = "contract " + name + sourseCode
        return code, name

    def create_contract(self, code):
        data = {"Wallet": "", "ApplicationId": 1,
                "Value": code,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        result = actions.call_contract(self.url, self.pr_key, "NewContract",
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def call_contract(self, name, data):
        result = actions.call_contract(self.url, self.pr_key, name,
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def check_contract(self, sourse, check_point):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        res = actions.call_contract(self.url, self.pr_key, name, {}, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertIn(check_point, result["result"], "ERROR: " +\
                           str(result))

    def call(self, name, data):
        result = actions.call_contract(self.url, self.pr_key, name, data, self.token)
        status = actions.tx_status(self.url, self.wait, result, self.token)
        return status

    def check_contract_with_data(self, sourse, data, check_point):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        res = actions.call_contract(self.url, self.pr_key, name, data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertIn(check_point, result["result"], "error")

    @pytest.mark.parametrize("name,sourse,e_result", tools.json_to_list(contracts["simple"]))
    def test_simple(self, name, sourse, e_result):
        code, c_name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        res = actions.call_contract(self.url, self.pr_key, c_name, {}, self.token)
        c_result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertIn(e_result, c_result["result"], "ERROR:\n name: " + name + '\n' +\
                           'expected result: ' + str(e_result) + '\n' +\
                           'current result: ' + str(c_result))

    def test_contract_langRes(self):
        data = {"Name": "test",
                "Trans": "{\"en\": \"test_en\", \"de\" : \"test_de\"}"}
        result = actions.call_contract(self.url, self.pr_key, "NewLang", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        contract = self.contracts["langRes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_dbInsert(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test", "ApplicationId": 1,
                "Columns": columns,
                "Permissions": permission}
        result = actions.call_contract(self.url, self.pr_key, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_dbUpdate(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test", "ApplicationId":1,
                "Columns": columns,
                "Permissions": permission}
        result = actions.call_contract(self.url, self.pr_key, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdate"]
        self.check_contract(contract["code"], contract["asert"])
        

    def test_contracts_dbUpdateExt(self):
        columns = """[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]"""
        permission = """{"insert": "true",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "test", "ApplicationId": 1,
                "Columns": columns,
                "Permissions": permission}
        result = actions.call_contract(self.url, self.pr_key, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdateExt"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_callContract(self):
        contract = self.contracts["myContract"]
        code = "contract MyContract" + contract["code"]
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = actions.call_contract(self.url, self.pr_key, "NewContract", data, self.token)
        time.sleep(10)
        contract = self.contracts["callContract"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sys_var_role_id_readonly(self):
        sys_var_name = "$block"
        contrac_name = tools.generate_random_name()
        value = "contract con_" + contrac_name + " { data{ } conditions{ } action{ " + sys_var_name + " = 5 } }"
        data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
        result = actions.call_contract(self.url, self.pr_key, "NewContract", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        print("tx", tx)
        exp_result = "system variable " + sys_var_name + " cannot be changed"
        msg = "system variable " + sys_var_name + " was been changed!"
        self.unit.assertEqual(tx["error"], exp_result, msg)

    def get_metrics(self, ecosystem_num, metric_name):
        # get metrics count
        res = actions.get_list(self.url, "metrics", self.token)
        i = 0
        while i < len(res['list']):
            if (int(res['list'][i]['key']) == int(ecosystem_num)) and (str(res['list'][i]['metric']) == str(metric_name)):
                return res['list'][i]['value']
            i += 1

    def test_z1_db_select_metrics_min(self):
         # func generate contract which return block_id and increment count blocks
        def wait_block_id(old_block_id, limit):
            while True:
                if old_block_id == limit:
                    break
                contracName = tools.generate_random_name()
                value = "contract con_" + contrac_name + " {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
                data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
                result = actions.call_contract(self.url, self.pr_key, "NewContract", data,
                                               self.token)
                tx = actions.tx_status(self.url, self.wait, result, self.token)
                current_block_id = int(tx["blockid"])
                self.unit.assertGreater(current_block_id, 0, "BlockId is not generated: " +\
                                        str(tx))
                old_block_id = current_block_id

        # generate contract which return count blocks in blockchain
        contrac_name = tools.generate_random_name()
        value = "contract con_" + contrac_name +\
         " {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
        data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
        result = actions.call_contract(self.url, self.pr_key, "NewContract", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        current_block_id = int(tx["blockid"])
        self.unit.assertGreater(current_block_id, 0, "BlockId is not generated: " + str(tx))
        # wait until generated 100 blocks
        if current_block_id < 100:
            wait_block_id(current_block_id, 100)
        # wait until generated multiples of 100 blocks
        if (current_block_id % 100 >= 90):
            count = current_block_id + (100 - (current_block_id % 100))
            wait_block_id(current_block_id, count)
        # test
        ecosystem_tx = self.get_metrics(1, "ecosystem_tx")
        contract = self.contracts["dbSelectMetricsMin"]
        self.check_contract(contract["code"], str(ecosystem_tx))

    def test_z2_db_select_metrics_max(self):
        # Run test after test_z1_db_select_metrics_min
        ecosystem_members = self.get_metrics(1, "ecosystem_members")
        contract = self.contracts["dbSelectMetricsMax"]
        self.check_contract(contract["code"], str(ecosystem_members))

    def test_z3_db_select_metrics_max(self):
        # Run test after test_z1_db_select_metrics_min
        ecosystem_pages = self.get_metrics(1, "ecosystem_pages")
        contract = self.contracts["dbSelectMetricsAvg"]
        self.check_contract(contract["code"], str(ecosystem_pages))

    def test_get_history_contract(self):
        # create contract
        replaced_string = "old_var"
        code = """
        { 
            data{}
            conditions{}
            action{ var %s int }
        }
        """ % replaced_string
        code, name = self.generate_name_and_code(code)
        self.create_contract(code)
        # change contract
        id = actions.get_object_id(self.url, name, "contracts", self.token)
        new_code = code.replace(replaced_string, "new_var")
        data = {"Id": id,
                "Value": new_code}
        self.call_contract("EditContract", data)
        # test
        data = {"Table": "contracts", "ID": id}
        contract = self.contracts["getHistory"]
        self.check_contract_with_data(contract["code"], data, replaced_string)

    def test_get_history_page(self):
        # create page
        name = tools.generate_random_name()
        page = "Div(Body: Hello)"
        data = {"ApplicationId": "1",
                "Name": name,
                "Value": page,
                "Menu": "default_menu",
                "Conditions": "true"}
        self.call_contract("NewPage", data)
        # change page
        id = actions.get_object_id(self.url, name, "pages", self.token)
        new_value_page = page.replace("Hello", "new_var")
        data = {"Id": id,
                "Value": new_value_page}
        self.call_contract("EditPage", data)
        # test
        data = {"Table": "pages", "ID": id}
        contract = self.contracts["getHistory"]
        self.check_contract_with_data(contract["code"], data, page)

    def test_sys_var_stack(self):
        # This test has not a fixture
        innerBody = """
                {
                data{}
                conditions{}
                action {
                    $result = $stack
                    }
                }
                """
        inner_code, inner_name = self.generate_name_and_code(innerBody)
        self.create_contract(inner_code)
        outer_body = """
                {
                data{}
                conditions{}
                action {
                    var par map
                    var res string
                    res = CallContract("%s", par)
                    $result = res
                    }
                }
                """ % inner_name
        outer_code, outer_name = self.generate_name_and_code(outer_body)
        self.create_contract(outer_code)
        data = {}
        res = self.call(outer_name, data)
        must_be = "[@1" + outer_name + " @1" + inner_name +"]"
        self.unit.assertEqual(must_be, res["result"], "test_sys_var_stack is failed!")

    def test_get_history_row_menu(self):
        # create menu
        rollc_before = db.get_max_id_from_table(self.db1, "rollback_tx")
        name = tools.generate_random_name()
        menu = "This is new menu"
        data = {"Name": name,
                "Value": menu,
                "Conditions": "true"}
        self.call_contract("NewMenu", data)
        rollc_after = db.get_max_id_from_table(self.db1, "rollback_tx")
        # change menu
        id = actions.get_object_id(self.url, name, "menu", self.token)
        new_value_menu = menu.replace("new menu", "new_var")
        data = {"Id": id,
                "Value": new_value_menu}
        self.call_contract("EditMenu", data)
        # test
        query = """SELECT id FROM "rollback_tx" WHERE table_name = '1_menu' AND data='' AND id >= %s AND id <= %s""" % (
            rollc_before, rollc_after)
        rollback_id = db.submit_query(query, self.db1)[0][0]
        data = {"Table": "menu", "ID": id, "rID": rollback_id}
        contract = self.contracts["getHistoryRow"]
        self.check_contract_with_data(contract["code"], data, menu)

    def test_get_history_row_block(self):
        # create block
        rollc_before = db.get_max_id_from_table(self.db1, "rollback_tx")
        name = tools.generate_random_name()
        block = "Div(Body: Hello)"
        data = {"ApplicationId": "1",
                "Name": name,
                "Value": block,
                "Conditions": "true"}
        self.call_contract("NewBlock", data)
        rollc_after = db.get_max_id_from_table(self.db1, "rollback_tx")
        # change block
        id = actions.get_object_id(self.url, name, "blocks", self.token)
        new_value_block = block.replace("Hello", "new_var")
        data = {"Id": id,
                "Value": new_value_block}
        self.call_contract("EditBlock", data)
        # test
        query = """SELECT id FROM "rollback_tx" WHERE table_name = '1_blocks' AND data='' AND id >= %s AND id <= %s""" % (
            rollc_before, rollc_after)
        rollback_id = db.submit_query(query, self.db1)[0][0]
        data = {"Table": "blocks", "ID": id, "rID": rollback_id}
        contract = self.contracts["getHistoryRow"]
        self.check_contract_with_data(contract["code"], data, block)