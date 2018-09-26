import unittest
import json
import time
import pytest

from libs import actions
from libs import db
from libs import tools


class TestSimvolio():
    contracts = tools.read_fixtures("simvolio")
    wait = tools.read_config("test")["wait_tx_status"]
    config = tools.read_config("nodes")
    unit = unittest.TestCase()

    def setup(self):
        print("setup class")
        self.url = self.config[1]["url"]
        self.prKey = self.config[0]['private_key']
        self.db1 = self.config[0]['db']
        data = actions.login(self.url, self.prKey, 0)
        self.token = data["jwtToken"]

    def assert_tx_in_block(self, result, jwtToken):
        self.unit.assertIn("hash", result)
        status = actions.tx_status(self.url, self.wait, result['hash'], jwtToken)
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
        result = actions.call_contract(self.url, self.prKey, "NewContract",
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def call_contract(self, name, data):
        result = actions.call_contract(self.url, self.prKey, name,
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def check_contract(self, sourse, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        res = actions.call_contract(self.url, self.prKey, name, {}, self.token)
        hash = res["hash"]
        result = actions.tx_status(self.url, self.wait, hash, self.token)
        self.unit.assertIn(checkPoint, result["result"], "error")

    def call(self, name, data):
        result = actions.call_contract(self.url, self.prKey, name, data, self.token)
        status = actions.tx_status(self.url, self.wait, result['hash'], self.token)
        return status

    def check_contract_with_data(self, sourse, data, checkPoint):
        code, name = self.generate_name_and_code(sourse)
        self.create_contract(code)
        res = actions.call_contract(self.url, self.prKey, name, data, self.token)
        hash = res["hash"]
        result = actions.tx_status(self.url, self.wait, hash, self.token)
        self.unit.assertIn(checkPoint, result["result"], "error")

    @pytest.mark.parametrize("name,code,result", tools.json_to_list(contracts["simple"]))
    def test_contract_db_find(self, name, code, result):
        print("name", name)
        print("result", result)
        self.check_contract(code, result)

    def test_contract_langRes(self):
        data = {"ApplicationId": 1,
                "Name": "test",
                "Trans": "{\"en\": \"test_en\", \"de\" : \"test_de\"}"}
        result = actions.call_contract(self.url, self.prKey, "NewLang", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
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
        result = actions.call_contract(self.url, self.prKey, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
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
        result = actions.call_contract(self.url, self.prKey, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
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
        result = actions.call_contract(self.url, self.prKey, "NewTable", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
        contract = self.contracts["dbInsert"]
        self.check_contract(contract["code"], contract["asert"])
        contract = self.contracts["dbUpdateExt"]
        self.check_contract(contract["code"], contract["asert"])

    def test_contract_callContract(self):
        contract = self.contracts["myContract"]
        code = "contract MyContract" + contract["code"]
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = actions.call_contract(self.url, self.prKey, "NewContract", data, self.token)
        time.sleep(10)
        contract = self.contracts["callContract"]
        self.check_contract(contract["code"], contract["asert"])

    def test_sys_var_role_id_readonly(self):
        sysVarName = "$block"
        contracName = tools.generate_random_name()
        value = "contract con_" + contracName + " { data{ } conditions{ } action{ " + sysVarName + " = 5 } }"
        data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
        result = actions.call_contract(self.url, self.prKey, "NewContract", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
        print("tx", tx)
        expResult = "system variable " + sysVarName + " cannot be changed"
        msg = "system variable " + sysVarName + " was been changed!"
        self.unit.assertEqual(tx["error"], expResult, msg)

    def getMetrics(self, ecosystemNum, metricName):
        # get metrics count
        res = actions.get_list(self.url, "metrics", self.token)
        i = 0
        while i < len(res['list']):
            if (int(res['list'][i]['key']) == int(ecosystemNum)) and (str(res['list'][i]['metric']) == str(metricName)):
                return res['list'][i]['value']
            i += 1

    def test_z1_dbSelectMetricsMin(self):
        # func generate contract which return block_id and increment count blocks
        def waitBlockId(old_block_id, limit):
            while True:
                if old_block_id == limit:
                    break
                contracName = tools.generate_random_name()
                value = "contract con_" + contracName + " {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
                data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
                result = actions.call_contract(self.url, self.prKey, "NewContract", data, self.token)
                tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
                current_block_id = int(tx["blockid"])
                self.unit.assertGreater(current_block_id, 0, "BlockId is not generated: " + str(tx))
                old_block_id = current_block_id

        # generate contract which return count blocks in blockchain
        contracName = tools.generate_random_name()
        value = "contract con_" + contracName + " {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
        data = {"Value": value, "ApplicationId": 1, "Conditions": "true"}
        result = actions.call_contract(self.url, self.prKey, "NewContract", data, self.token)
        tx = actions.tx_status(self.url, self.wait, result['hash'], self.token)
        current_block_id = int(tx["blockid"])
        self.unit.assertGreater(current_block_id, 0, "BlockId is not generated: " + str(tx))
        # wait until generated 100 blocks
        if current_block_id < 100:
            waitBlockId(current_block_id, 100)
        # wait until generated multiples of 100 blocks
        if (current_block_id % 100 >= 90):
            count = current_block_id + (100 - (current_block_id % 100))
            waitBlockId(current_block_id, count)
        # test
        ecosystem_tx = self.getMetrics(1, "ecosystem_tx")
        contract = self.contracts["dbSelectMetricsMin"]
        self.check_contract(contract["code"], str(ecosystem_tx))

    def test_z2_dbSelectMetricsMax(self):
        # Run test after test_z1_dbSelectMetricsMin
        ecosystem_members = self.getMetrics(1, "ecosystem_members")
        contract = self.contracts["dbSelectMetricsMax"]
        self.check_contract(contract["code"], str(ecosystem_members))

    def test_z3_dbSelectMetricsAvg(self):
        # Run test after test_z1_dbSelectMetricsMin
        ecosystem_pages = self.getMetrics(1, "ecosystem_pages")
        contract = self.contracts["dbSelectMetricsAvg"]
        self.check_contract(contract["code"], str(ecosystem_pages))

    def test_getHistoryContract(self):
        # create contract
        replacedString = "old_var"
        code = """
        { 
            data{}
            conditions{}
            action{ var %s int }
        }
        """ % replacedString
        code, name = self.generate_name_and_code(code)
        self.create_contract(code)
        # change contract
        id = actions.get_object_id(self.url, name, "contracts", self.token)
        newCode = code.replace(replacedString, "new_var")
        data = {"Id": id,
                "Value": newCode}
        self.call_contract("EditContract", data)
        # test
        data = {"Table": "contracts", "ID": id}
        contract = self.contracts["getHistory"]
        self.check_contract_with_data(contract["code"], data, replacedString)

    def test_getHistoryPage(self):
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
        newValuePage = page.replace("Hello", "new_var")
        data = {"Id": id,
                "Value": newValuePage}
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
        innerCode, innerName = self.generate_name_and_code(innerBody)
        self.create_contract(innerCode)
        outerBody = """
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
                """ % innerName
        outerCode, outerName = self.generate_name_and_code(outerBody)
        self.create_contract(outerCode)
        data = {"Wallet": "", "ApplicationId": 1,
                "Value": outerCode,
                "Conditions": "ContractConditions(`MainCondition`)"}
        res = self.call(outerName, data)
        mustBe = "[@1" + outerName + " CallContract @1" + innerName + "]"
        self.unit.assertEqual(mustBe, res["result"], "test_sys_var_stack is failed!")

    def test_getHistoryRowMenu(self):
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
        newValueMenu = menu.replace("new menu", "new_var")
        data = {"Id": id,
                "Value": newValueMenu}
        self.call_contract("EditMenu", data)
        # test
        query = """SELECT id FROM "rollback_tx" WHERE table_name = '1_menu' AND data='' AND id >= %s AND id <= %s""" % (
            rollc_before, rollc_after)
        rollback_id = db.submit_query(query, self.db1)[0][0]
        data = {"Table": "menu", "ID": id, "rID": rollback_id}
        contract = self.contracts["getHistoryRow"]
        self.check_contract_with_data(contract["code"], data, menu)

    def test_getHistoryRowBlock(self):
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
        newValueBlock = block.replace("Hello", "new_var")
        data = {"Id": id,
                "Value": newValueBlock}
        self.call_contract("EditBlock", data)
        # test
        query = """SELECT id FROM "rollback_tx" WHERE table_name = '1_blocks' AND data='' AND id >= %s AND id <= %s""" % (
            rollc_before, rollc_after)
        rollback_id = db.submit_query(query, self.db1)[0][0]
        data = {"Table": "blocks", "ID": id, "rID": rollback_id}
        contract = self.contracts["getHistoryRow"]
        self.check_contract_with_data(contract["code"], data, block)