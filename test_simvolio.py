import unittest
import json
import time
import pytest

from libs import actions, db, tools, api


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
        self.unit.assertIn(check_point, result["result"], "ERROR: " + \
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

    def test_contract_dbFind(self):
        contract = self.contracts["dbFind"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_toUpper(self):
        contract = self.contracts["toUpper"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_elseif(self):
        contract = self.contracts["elseif"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_blockTime(self):
        contract = self.contracts["blockTime"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ecosysParam(self):
        contract = self.contracts["ecosysParam"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_ifMap(self):
        contract = self.contracts["ifMap"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_dbRow(self):
        contract = self.contracts["dbRow"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_evalCondition(self):
        contract = self.contracts["evalCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_validateCondition(self):
        contract = self.contracts["validateCondition"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_addressToId(self):
        contract = self.contracts["addressToId"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_idToAddress(self):
        contract = self.contracts["idToAddress"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_one(self):
        contract = self.contracts["one"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_row(self):
        contract = self.contracts["row"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_contains(self):
        contract = self.contracts["contains"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_float(self):
        contract = self.contracts["float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hasPrefix(self):
        contract = self.contracts["hasPrefix"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_hexToBytes(self):
        contract = self.contracts["hexToBytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_int(self):
        contract = self.contracts["int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_join(self):
        contract = self.contracts["join"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_split(self):
        contract = self.contracts["split"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_len(self):
        contract = self.contracts["len"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_pubToID(self):
        contract = self.contracts["pubToID"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_replace(self):
        contract = self.contracts["replace"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_size(self):
        contract = self.contracts["size"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sha256(self):
        contract = self.contracts["sha256"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sprintf(self):
        contract = self.contracts["sprintf"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_str(self):
        contract = self.contracts["str"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_substr(self):
        contract = self.contracts["substr"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamString(self):
        contract = self.contracts["sysParamString"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sysParamInt(self):
        contract = self.contracts["sysParamInt"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getContractByName(self):
        contract = self.contracts["getContractByName"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_random(self):
        contract = self.contracts["random"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getBlock(self):
        contract = self.contracts["getBlock"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_bool(self):
        contract = self.contracts["type_bool"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_bytes(self):
        contract = self.contracts["type_bytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_int(self):
        contract = self.contracts["type_int"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_address(self):
        contract = self.contracts["type_address"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_array(self):
        contract = self.contracts["type_array"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_map(self):
        contract = self.contracts["type_map"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_money(self):
        contract = self.contracts["type_money"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_float(self):
        contract = self.contracts["type_float"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_type_string(self):
        contract = self.contracts["type_string"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getColumnType(self):
        contract = self.contracts["getColumnType"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_decodeBase64(self):
        contract = self.contracts["decodeBase64"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_encodeBase64(self):
        contract = self.contracts["encodeBase64"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_jsonEncode(self):
        contract = self.contracts["jsonEncode"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_jsonDecode(self):
        contract = self.contracts["jsonDecode"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_bytesToString(self):
        contract = self.contracts["bytesToString"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_stringToBytes(self):
        contract = self.contracts["stringToBytes"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_append(self):
        contract = self.contracts["append"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_getMapKeys(self):
        contract = self.contracts["getMapKeys"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_sortedKeys(self):
        contract = self.contracts["sortedKeys"]
        self.check_contract(contract["code"], contract["asert"])

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
        data = {"Name": "test", "ApplicationId": 1,
                "Columns": columns,
                "Permissions": permission}
        result = actions.call_contract(self.url, self.pr_key, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result, self.token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdate"]
        self.check_contract(contract["code"], contract["asert"])
        list = actions.get_list(self.url, "test", self.token)['list']
        for el in range(len(list)):
            if int(list[el]['id']) == 1:
                self.unit.assertEqual('updated', list[el]['test'], 'Failed. dbUpdate Error!')
                break

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
        contract = self.contracts["callContract"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sys_vars_readonly(self):
        var_list = [
            '$time',
            '$ecosystem_id',
            '$block',
            '$key_id',
            '$block_key_id',
            '$block_time',
            '$original_contract',
            '$this_contract',
            '$guest_key',
            '$stack',
        ]
        expexted_dict = {}
        actual_dict = {}
        for i in range(len(var_list)):
            sys_var_name = var_list[i]
            print(sys_var_name)
            contrac_name = tools.generate_random_name()
            value = "contract con_" + contrac_name + " { data{ } conditions{ } action{ " + sys_var_name + " = 5 } }"
            data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
            result = actions.call_contract(self.url, self.pr_key, "NewContract", data, self.token)
            tx = actions.tx_status(self.url, self.wait, result, self.token)
            exp_result = "system variable " + sys_var_name + " cannot be changed"
            expexted_dict[i] = exp_result
            actual_dict[i] = tx["error"]
        self.unit.assertDictEqual(expexted_dict, actual_dict, 'Dictionaries is different')


    def get_metrics(self, ecosystem_num, metric_name):
        # get metrics count
        res = actions.get_list(self.url, "metrics", self.token)
        i = 0
        while i < len(res['list']):
            if (int(res['list'][i]['key']) == int(ecosystem_num)) and (
                    str(res['list'][i]['metric']) == str(metric_name)):
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
                self.unit.assertGreater(current_block_id, 0, "BlockId is not generated: " + \
                                        str(tx))
                old_block_id = current_block_id

        # generate contract which return count blocks in blockchain
        contrac_name = tools.generate_random_name()
        value = "contract con_" + contrac_name + \
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
        must_be = "[@1" + outer_name + " @1" + inner_name + "]"
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