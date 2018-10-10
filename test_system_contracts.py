import unittest
import json
import os
import time

from libs import actions, db, tools


class TestSystemContracts():
    config = tools.read_config("nodes")
    url = config[0]["url"]
    wait = tools.read_config("test")["wait_tx_status"]
    pr_key = config[0]['private_key']
    db = config[0]["db"]
    data = actions.login(url, pr_key, 0)
    token = data["jwtToken"]

    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, result, jwt_token):
        status = actions.tx_status(self.url, self.wait, result, jwt_token)
        if len(status['blockid']) > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return {"blockid": int(status["blockid"]), "error": "0"}
        else:
            return {"blockid": 0, "error": status["errmsg"]["error"]}

    def call(self, name, data):
        resp = actions.call_contract(self.url, self.pr_key, name, data, self.token)
        resp = self.assert_tx_in_block(resp, self.token)
        return resp

    def assert_multi_tx_in_block(self, result, jwt_token):
        self.unit.assertIn("hashes", result)
        hashes = result['hashes']
        result = actions.tx_status_multi(self.url, self.wait, hashes, jwt_token)
        for status in result.values():
            self.unit.assertNotIn('errmsg', status)
            self.unit.assertGreater(int(status["blockid"]), 0,
                               "BlockID not generated")

    def callMulti(self, name, data, sleep):
        resp = actions.call_multi_contract(self.url, self.pr_key, name, data, self.token)
        time.sleep(sleep)
        resp = self.assert_multi_tx_in_block(resp, self.token)
        return resp

    def wait_block_id(self, old_block_id, limit):
        while True:
            # add contract, which get block_id
            body = "{\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
            code, name = tools.generate_name_and_code(body)
            data = {"Value": code, "ApplicationId": 1,
                    "Conditions": "true"}
            res = self.call("NewContract", data)
            self.unit.assertGreater(res["blockid"], 0, "BlockId is not generated: " + str(res))
            currrent_block_id = res["blockid"]
            expected_block_id = old_block_id + limit + 1  # +1 spare block
            if currrent_block_id == expected_block_id:
                break

    def test_create_ecosystem(self):
        data = {"Name": "Ecosys_" + tools.generate_random_name()}
        res = self.call("NewEcosystem", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # !!!
    def test_edit_application(self):
        name = "App" + tools.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_object_id(self.url, name, "applications", self.token)
        data = {"ApplicationId": id, "Conditions": "false"}
        res = self.call("EditApplication", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_activate_application(self):
        name = "App" + tools.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_object_id(self.url, name, "applications", self.token)
        data_deact = {"ApplicationId": id, "Value": 0}
        res = self.call("DelApplication", data_deact)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_act = {"ApplicationId": id, "Value": 1}
        res = self.call("DelApplication", data_act)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_export_application(self):
        name = "App" + tools.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_object_id(self.url, name, "applications", self.token)
        data_deact = {"ApplicationId": id}
        res = self.call("ExportNewApp", data_deact)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # !!!
    def test_edit_ecosystem_name(self):
        id = 1
        data = {"EcosystemID": id, "NewName": "Ecosys_" + tools.generate_random_name()}
        res_block_id = self.call("EditEcosystemName", data)
        self.unit.assertGreater(res_block_id["blockid"], 0,
                           "BlockId is not generated: " + str(res_block_id))

    def test_edit_ecosystem_name_incorrect_id(self):
        id = 500
        data = {"EcosystemID": id, "NewName": "ecosys_" + tools.generate_random_name()}
        res = self.call("EditEcosystemName", data)
        self.unit.assertEqual("Ecosystem " + str(id) + " does not exist", res["error"])

    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "1000"}
        res = self.call("MoneyTransfer", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))


    def test_money_transfer_incorrect_wallet(self):
        wallet = "0005-2070-2000-0006"
        msg = "Recipient " + wallet + " is invalid"
        data = {"Recipient": wallet, "Amount": "1000"}
        ans = self.call("MoneyTransfer", data)
        self.unit.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_zero_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "0"}
        ans = self.call("MoneyTransfer", data)
        self.unit.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_negative_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "-1000"}
        ans = self.call("MoneyTransfer", data)
        self.unit.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_amount_as_string(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "can't convert ttt to decimal"
        data = {"Recipient": wallet, "Amount": "ttt"}
        ans = self.call("MoneyTransfer", data)
        self.unit.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_with_comment(self):
        wallet = "0005-2070-2000-0006-0200"
        data = {"Recipient": wallet, "Amount": "1000", "Comment": "Test"}
        res = self.call("MoneyTransfer", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_contract(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_contract_exists_name(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewContract", data)
        msg = "Contract " + name + " already exists"
        self.unit.assertEqual(ans["error"], msg, "Incorrect message: " + str(ans))

    def test_new_contract_without_name(self):
        code = "contract {data { }    conditions {    }    action {    }    }"
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        ans = self.call("NewContract", data)
        self.unit.assertIn("must be the name", ans["error"],
                      "Incorrect message: " + str(ans))

    def test_new_contract_incorrect_condition(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "condition"}
        ans = self.call("NewContract", data)
        self.unit.assertEqual("unknown identifier condition",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract_incorrect_condition(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": actions.get_contract_id(self.url, name, self.token),
                 "Value": code, "Conditions": "tryam",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2)
        self.unit.assertEqual("unknown identifier tryam",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract_incorrect_condition1(self):
        wallet = "0005"
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": actions.get_contract_id(self.url, name, self.token),
                 "Value": code, "Conditions": "true",
                 "WalletId": wallet}
        ans = self.call("EditContract", data2)
        msg = "New contract owner " + wallet + " is invalid"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract(self):
        wallet = "0005-2070-2000-0006-0200"  # ??
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_name_of_contract(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        code1, name1 = tools.generate_name_and_code("")
        data2 = {"Id": actions.get_contract_id(self.url, name, self.token),
                 "Value": code1, "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2)
        self.unit.assertEqual("Contracts or functions names cannot be changed",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_contract(self):
        code, name = tools.generate_name_and_code("")
        id = "9999"
        data2 = {"Id": id, "Value": code, "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2)
        self.unit.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_activate_contract(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_contract_id(self.url, name, self.token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_activate_incorrect_contract(self):
        id = "99999"
        data = {"Id": id}
        ans = self.call("ActivateContract", data)
        msg = "Contract " + id + " does not exist"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_deactivate_contract(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_contract_id(self.url, name, self.token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2)
        # self.unit.assertGreater(res["blockid"], 0,        self.conf = self.config.readMainConfig()

    def test_deactivate_incorrect_contract(self):
        id = "99999"
        data = {"Id": id}
        ans = self.call("DeactivateContract", data)
        self.unit.assertEqual("Contract " + id + " does not exist",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_parameter(self):
        data = {"Name": "Par_" + tools.generate_random_name(), "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_parameter_exist_name(self):
        name = "Par_" + tools.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        msg = "Parameter " + name + " already exists"
        ans = self.call("NewParameter", data)
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_parameter_incorrect_condition(self):
        condition = "tryam"
        data = {"Name": "Par_" + tools.generate_random_name(), "Value": "test", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewParameter", data)
        self.unit.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_parameter(self):
        id = "99999"
        data2 = {"Id": id, "Value": "test_edited", "Conditions": "true"}
        ans = self.call("EditParameter", data2)
        self.unit.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_parameter_incorrect_condition(self):
        name = "Par_" + tools.generate_random_name()
        condition = "tryam"
        id = actions.get_parameter_id(self.url, name, self.token)
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        res = self.call("NewParameter", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": id, "Value": "test_edited", "Conditions": condition}
        ans = self.call("EditParameter", data2)
        self.unit.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_menu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        m_content = actions.get_content(self.url, "menu", name, "", 1, self.token)
        self.unit.assertEqual(m_content, content)

    def test_new_menu_exist_name(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewMenu", data)
        self.unit.assertEqual("Menu " + name + " already exists",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_menu_incorrect_condition(self):
        name = "Menu_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewMenu", data)
        self.unit.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_menu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "menu", self.token)
        data_edit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        res = self.call("EditMenu", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        m_content = actions.get_content(self.url, "menu", name, "", 1, self.token)
        self.unit.assertEqual(m_content, content)

    def test_edit_incorrect_menu(self):
        id = "99999"
        data_edit = {"Id": id, "Value": "ItemEdited", "Conditions": "true"}
        ans = self.call("EditMenu", data_edit)
        msg = "Item " + id + " has not been found"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_menu_incorrect_condition(self):
        name = "Menu_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "menu", self.token)
        data_edit = {"Id": count, "Value": "ItemEdited", "Conditions": condition}
        ans = self.call("EditMenu", data_edit)
        msg = "unknown identifier " + condition
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_append_menu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "menu", self.token)
        data_edit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        res = self.call("AppendMenu", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_append_incorrect_menu(self):
        id = "999"
        data_edit = {"Id": id, "Value": "AppendedItem", "Conditions": "true"}
        ans = self.call("AppendMenu", data_edit)
        msg = "Item " + id + " has not been found"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_page(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(cont['tree'], content)

    def test_new_page_exist_name(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewPage", data)
        msg = "Page " + name + " already exists"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_page_incorrect_condition(self):
        name = "Page_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition, "Menu": "default_menu"}
        ans = self.call("NewPage", data)
        msg = "unknown identifier " + condition
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_page(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_edit = {"Id": actions.get_count(self.url, "pages", self.token),
                    "Value": "Good by page!", "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("EditPage", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        p_content = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(p_content['tree'], content)

    def test_edit_page_with_validate_count(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "Conditions": "true",
                "ValidateCount": 6, "Menu": "default_menu",
                "ApplicationId": 1}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_edit = {"Id": actions.get_count(self.url, "pages", self.token),
                    "Value": "Good by page!", "Conditions": "true",
                    "ValidateCount": 1, "Menu": "default_menu"}
        res = self.call("EditPage", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        p_content = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(p_content['tree'], content)

    def test_edit_incorrect_page(self):
        id = "99999"
        data_edit = {"Id": id, "Value": "Good by page!",
                    "Conditions": "true", "Menu": "default_menu"}
        ans = self.call("EditPage", data_edit)
        self.unit.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_page_incorrect_condition(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!",
                "Conditions": "true", "Menu": "default_menu",
                "ApplicationId": 1}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        condition = "Tryam"
        data_edit = {"Id": actions.get_count(self.url, "pages", self.token),
                    "Value": "Good by page!", "Conditions": condition,
                    "Menu": "default_menu"}
        ans = self.call("EditPage", data_edit)
        self.unit.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_append_page(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello!", "Conditions": "true",
                "Menu": "default_menu", "ApplicationId": 1}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "pages", self.token)
        data_edit = {"Id": actions.get_count(self.url, "pages", self.token),
                    "Value": "Good by!", "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("AppendPage", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        p_content = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(p_content['tree'], content)

    def test_append_page_incorrect_id(self):
        id = "9999"
        data_edit = {"Id": id, "Value": "Good by!", "Conditions": "true",
                    "Menu": "default_menu"}
        ans = self.call("AppendPage", data_edit)
        msg = "Item " + id + " has not been found"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_block(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_block_exist_name(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewBlock", data)
        self.unit.assertEqual("Block " + name + " already exists",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_block_incorrect_condition(self):
        name = "Block_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewBlock", data)
        msg = "unknown identifier " + condition
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block_incorrect_id(self):
        id = "9999"
        data_edit = {"Id": id, "Value": "Good by!", "Conditions": "true"}
        ans = self.call("EditBlock", data_edit)
        msg = "Item " + id + " has not been found"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "blocks", self.token)
        data_edit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        res = self.call("EditBlock", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_block_incorrect_condition(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "blocks", self.token)
        condition = "tryam"
        data_edit = {"Id": count, "Value": "Good by!", "Conditions": condition}
        ans = self.call("EditBlock", data_edit)
        msg = "unknown identifier " + condition
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "true"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        permission = """
        {"read" : "false", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        table_name = "tab_" + tools.generate_random_name()
        data = {"Name": table_name,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.unit.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + table_name + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [{'tag': 'text', 'text': 'Access denied'}]
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(cont['tree'], content)

    def test_new_table_not_readable(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        permission = """
        {"read" : "true", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        table_name = "tab_" + tools.generate_random_name()
        data = {"Name": table_name,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.unit.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new contract, which added record in table
        code = """{
        data {}    
        conditions {}    
        action {
            DBInsert("%s", {text: "text1", num: "num1"})    
        }
        }""" % table_name
        code, name = tools.generate_name_and_code(code)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # call contract
        res = self.call(name, "")
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + table_name + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [['num1', '1']]
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(cont['tree'][0]['attr']['data'], content)

    def test_new_table_not_readable_all_columns(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "false"}}
        ]"""
        permission = """
        {"read" : "true", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        table_name = "tab_" + tools.generate_random_name()
        data = {"Name": table_name,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.unit.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + table_name + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [{'tag': 'text', 'text': 'Access denied'}]
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(cont['tree'], content)

    def test_new_table_not_readable_one_column(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        permission = """
        {"read" : "true", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        table_name = "tab_" + tools.generate_random_name()
        data = {"Name": table_name,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data)
        self.unit.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new contract, which added record in table
        code = """{
        data {}    
        conditions {}    
        action {
            DBInsert("%s", {text: "text1", num: "num1"})    
        }
        }""" % table_name
        code, name = tools.generate_name_and_code(code)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # call contract
        res = self.call(name, "")
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + table_name + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [['num1', '1']]
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(cont['tree'][0]['attr']['data'], content)

    def test_new_table_joint(self):
        columns = ["varchar", "Myb", "MyD", "MyM", "MyT", "MyDouble", "MyC"]
        types = ["varchar", "json", "datetime", "money", "text", "double", "character"]
        dic_columns = {"ColumnsArr[]": len(columns), "ColumnsArr[0]": columns[0],
                      "ColumnsArr[1]": columns[1], "ColumnsArr[2]": columns[2],
                      "ColumnsArr[3]": columns[3], "ColumnsArr[4]": columns[4],
                      "ColumnsArr[5]": columns[5], "ColumnsArr[6]": columns[6]}
        dic_types = {"TypesArr[]": len(types), "TypesArr[0]": types[0],
                    "TypesArr[1]": types[1], "TypesArr[2]": types[2],
                    "TypesArr[3]": types[3], "TypesArr[4]": types[4],
                    "TypesArr[5]": types[5], "TypesArr[6]": types[6]}
        permission = """{"insert": "false", "update" : "true","new_column": "true"}"""
        data = {"ApplicationId": 1,
                "Name": "Tab_" + tools.generate_random_name(),
                "ColumnsArr": dic_columns,
                "TypesArr": dic_types,
                "InsertPerm": "true",
                "UpdatePerm": "true",
                "ReadPerm": "true",
                "NewColumnPerm": "true"}
        data.update(dic_columns)
        data.update(dic_types)
        res = self.call("NewTableJoint", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_table_incorrect_column_name_digit(self):
        column = """[{"name":"123","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        ans = self.call("NewTable", data)
        msg = "Column name cannot begin with digit"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_column_name_cyrillic(self):
        word = "привет"
        column = """[{"name":"%s","type":"varchar",
        "index": "1",  "conditions":"true"}]""" % word
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        ans = self.call("NewTable", data)
        msg = "Name " + word + " must only contain latin, digit and '_', '-' characters"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition1(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"" + condition + \
                      "\", \"update\" : \"true\", \"new_column\": \"true\"}"
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data)
        msg = "Condition " + condition + " is not allowed"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition2(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"" + \
                      condition + "\", \"new_column\": \"true\"}"
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data)
        msg = "Condition " + condition + " is not allowed"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition3(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"true\"," + \
                      " \"new_column\": \"" + condition + "\"}"
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data)
        msg = "Condition " + condition + " is not allowed"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_exist_name(self):
        name = "tab_" + tools.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\" : \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewTable", data)
        msg = "table " + name + " exists"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_name_cyrillic(self):
        name = "таблица"
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\" : \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        ans = self.call("NewTable", data)
        msg = "Name " + name + " must only contain latin, digit and '_', '-' characters"
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_identical_columns(self):
        name = "tab_" + tools.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}," + \
                  "{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\": \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        ans = self.call("NewTable", data)
        self.unit.assertEqual("There are the same columns", ans["error"],
                         "Incorrect message: " + str(ans))

    def test_edit_table(self):
        name = "Tab_" + tools.generate_random_name()
        columns = """[{"name": "MyName", "type": "varchar", "index": "1", "conditions": "true"}]"""
        permissions = """{"insert": "false", "update": "true", "new_column": "true"}"""
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_edit = {"Name": name,
                    "InsertPerm": "true",
                    "UpdatePerm": "true",
                    "ReadPerm": "true",
                    "NewColumnPerm": "true"}
        res = self.call("EditTable", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_column(self):
        name_tab = "Tab_" + tools.generate_random_name()
        columns = """[{"name": "MyName", "type":"varchar", "index": "1", "conditions": "true"}]"""
        permissions = """{"insert": "false", "update": "true", "new_column": "true"}"""
        data = {"ApplicationId": 1,
                "Name": name_tab,
                "Columns": columns,
                "Permissions": permissions, }
        res = self.call("NewTable", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col1 = {"TableName": name_tab,
                    "Name": "var",
                    "Type": "varchar",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res1 = self.call("NewColumn", data_col1)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col2 = {"TableName": name_tab,
                    "Name": "json",
                    "Type": "json",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res2 = self.call("NewColumn", data_col2)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col3 = {"TableName": name_tab,
                    "Name": "num",
                    "Type": "number",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res3 = self.call("NewColumn", data_col3)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col4 = {"TableName": name_tab,
                    "Name": "date",
                    "Type": "datetime",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res4 = self.call("NewColumn", data_col4)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col5 = {"TableName": name_tab,
                    "Name": "sum",
                    "Type": "money",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res5 = self.call("NewColumn", data_col5)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col6 = {"TableName": name_tab,
                    "Name": "name",
                    "Type": "text",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res6 = self.call("NewColumn", data_col6)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col7 = {"TableName": name_tab,
                    "Name": "length",
                    "Type": "double",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res7 = self.call("NewColumn", data_col7)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_col8 = {"TableName": name_tab,
                    "Name": "code",
                    "Type": "character",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res8 = self.call("NewColumn", data_col8)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_column(self):
        name_tab = "tab_" + tools.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\": \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": name_tab, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        name = "Col_" + tools.generate_random_name()
        data_col = {"TableName": name_tab, "Name": name, "Type": "number",
                   "UpdatePerm": "true", "ReadPerm": "true"}
        res = self.call("NewColumn", data_col)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data_edit = {"TableName": name_tab, "Name": name, "Type": "number",
                    "UpdatePerm": "false", "ReadPerm": "false"}
        res = self.call("EditColumn", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_lang(self):
        data = {"AppID": 1, "Name": "Lang_" + tools.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
        res = self.call("NewLang", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_lang_joint(self):
        data = {"ApplicationId": 1,
                "Name": "Lang_" + tools.generate_random_name(),
                "ValueArr": ["en", "ru"], "LocaleArr": ["Hi", "Привет"]}
        res = self.call("NewLangJoint", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_lang_joint(self):
        data = {"ApplicationId": 1,
                "Name": "Lang_" + tools.generate_random_name(),
                "ValueArr": ["en", "ru"], "LocaleArr": ["Hi", "Привет"]}
        res = self.call("NewLangJoint", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "languages", self.token)
        data_e = {"Id": count, "ValueArr": ["en", "de"],
                 "LocaleArr": ["Hi", "Hallo"]}
        res = self.call("EditLangJoint", data_e)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_lang(self):
        name = "Lang_" + tools.generate_random_name()
        data = {"AppID": 1, "Name": name, "ApplicationId": 1,
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("NewLang", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "languages", self.token)
        data_edit = {"Id": count, "Name": name, "AppID": 1,
                    "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("EditLang", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _new_sign(self):
        name = "Sign_" + tools.generate_random_name()
        value = "{\"forsign\":\"" + name + \
                "\", \"field\": \"" + name + "\", \"title\": \"" + name + \
                "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value, "Conditions": "true"}
        res = self.call("NewSign", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _new_sign_joint(self):
        name = "Sign_" + tools.generate_random_name()
        params = [{"name": "test", "text": "test"},
                  {"name": "test2", "text": "test2"}]
        values = ["one", "two"]
        data = {"Name": name, "Title": name, "ParamArr": params,
                "ValueArr": values, "Conditions": "true"}
        res = self.call("NewSignJoint", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _edit_sign_joint(self):
        name = "Sign_" + tools.generate_random_name()
        params = [{"name": "test", "text": "test"},
                  {"name": "test2", "text": "test2"}]
        values = ["one", "two"]
        data = {"Name": name, "Title": name, "ParamArr": params,
                "ValueArr": values, "Conditions": "true"}
        res = self.call("NewSignJoint", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "signatures", self.token)
        data_e = {"Id": count, "Title": "NewTitle", "Parameter": str(params),
                 "Conditions": "true"}
        resE = self.call("EditSignJoint", data_e)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _edit_sign(self):
        name = "Sign_" + tools.generate_random_name()
        value = "{\"forsign\":\"" + name + \
                "\", \"field\": \"" + name + "\", \"title\": \"" + name + \
                "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value, "Conditions": "true"}
        res = self.call("NewSign", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, "signatures", self.token)
        value_e = "{\"forsign\": \"" + name + "\", \"field\": \"" + \
                 name + "\", \"title\": \"" + name + \
                 "\", \"params\":[{\"name\": \"test1\", \"text\": \"test2\"}]}"
        data_edit = {"Id": count, "Value": value_e, "Conditions": "true"}
        res = self.call("EditSign", data_edit)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_app_param(self):
        name = "param_" + tools.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true"}
        res = self.call("NewAppParam", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_app_param(self):
        name = "param_" + tools.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true"}
        res = self.call("NewAppParam", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": 1, "Name": name, "Value": "myParamEdited", "Conditions": "true"}
        res = self.call("EditAppParam", data2)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_delayed_contracts(self):
        # add table for test
        column = """[{"name":"id_block","type":"number", "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "true", "update" : "true","new_column": "true"}"""
        table_name = "tab_delayed_" + tools.generate_random_name()
        data = {"Name": table_name, "Columns": column,
                "ApplicationId": 1, "Permissions": permission}
        res = self.call("NewTable", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # add contract which insert records in table in progress CallDelayedContract
        body = """
        {
            data{}
            conditions{}
            action {
                DBInsert("%s", {id_block: $block})
            }
        }
        """ % table_name
        code, contract_name = tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # NewDelayedContract
        new_limit = 3
        data = {"Contract": contract_name, "EveryBlock": "1",
                "Conditions": "true", "Limit": new_limit}
        res = self.call("NewDelayedContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        old_block_id = int(res["blockid"])
        # get record id of 'delayed_contracts' table for run EditDelayedContract
        res = actions.call_get_api(self.url + "/list/delayed_contracts", "", self.token)
        count = len(res["list"])
        id = res["list"][0]["id"]
        i = 1
        while i < count:
            if res["list"][i]["id"] > id:
                id = res["list"][i]["id"]
            i = i + 1
        # wait block_id until run CallDelayedContract
        self.wait_block_id(old_block_id, new_limit)
        # EditDelayedContract
        editLimit = 2
        data = {"Id": id, "Contract": contract_name, "EveryBlock": "1", "Conditions": "true", "Limit": editLimit}
        res = self.call("EditDelayedContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        old_block_id = res["blockid"]
        # wait block_id until run CallDelayedContract
        self.wait_block_id(old_block_id, editLimit)
        # verify records count in table
        count = actions.get_count(self.url, table_name, self.token)
        self.unit.assertEqual(int(count), new_limit + editLimit)

    def test_upload_binary(self):
        name = "image_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {'Name': name, 'ApplicationId': '1', 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary",
                                                data, self.token)
        res = self.assert_tx_in_block(resp, self.token)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_contract_recursive_call_by_name_action(self):
        contract_name = "recur_" + tools.generate_random_name()
        body = """
        {
        data { }
        conditions { }
        action {
            Println("hello1")
            %s()
            }
        }
        """ % contract_name
        code = tools.generate_code(contract_name, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        msg = "The contract can't call itself recursively"
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_by_name_conditions(self):
        contract_name = "recur_" + tools.generate_random_name()
        body = """
        {
        data { }
        conditions { 
            Println("hello1")
            %s()
            }
        action { }
        }
        """ % contract_name
        code = tools.generate_code(contract_name, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        msg = "The contract can't call itself recursively"
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_by_name_func_action(self):
        contract_name = "recur_" + tools.generate_random_name()
        body = """
        {
        func runContract() int {
            %s()
            }
        data { }
        conditions { }
        action {
            runContract()
            }
        }
        """ % contract_name
        code = tools.generate_code(contract_name, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        msg = "The contract can't call itself recursively"
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_action(self):
        contract_name = "recur_" + tools.generate_random_name()
        body = """
        {
        data { }
        conditions { }
        action {
            Println("hello1")
            var par map
            CallContract("%s", par)
            }
        }
        """ % contract_name
        code = tools.generate_code(contract_name, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contract_name, "")
        msg = "There is loop in @1" + contract_name + " contract"
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_conditions(self):
        contract_name = "recur_" + tools.generate_random_name()
        body = """
        {
        data { }
        conditions {
         Println("hello1")
            var par map
            CallContract("%s", par)
            }
        action { }
        }
        """ % contract_name
        code = tools.generate_code(contract_name, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contract_name, "")
        msg = "There is loop in @1" + contract_name + " contract"
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_func_conditions(self):
        contract_name = "recur_" + tools.generate_random_name()
        body = """
        {
        func runContract() int {
            var par map
            CallContract("%s", par)
            }
        data { }
        conditions {
            runContract()
            }
        action { }
        }
        """ % contract_name
        code = tools.generate_code(contract_name, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        res = self.call(contract_name, "")
        msg = "There is loop in @1" + contract_name + " contract"
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_memory_limit(self):
        # add contract with memory limit
        body = """
        {
        data {
            Count int "optional"
            }
        action {
            var a array
            while (true) {
                $Count = $Count + 1
                a[Len(a)] = JSONEncode(a)
                }
            }
        }
        """
        code, contract_name = tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        data = ""
        msg = "Memory limit exceeded"
        res = self.call(contract_name, data)
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_functions_recursive_limit(self):
        # add contract with recursive
        body = """
        {
        func myfunc(num int) int { 
            num = num + 1
            myfunc(num)
            }
        data{}
        conditions{}
        action {
            $a = 0
            myfunc($a)
            }
        }
        """
        code, contract_name = tools.generate_name_and_code(body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        data = ""
        msg = "max call depth"
        res = self.call(contract_name, data)
        self.unit.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_ei1_ExportNewApp(self):
        appID = 1
        data = {"ApplicationId": appID}
        res = self.call("ExportNewApp", data)
        self.unit.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_ei2_Export(self):
        appID = 1
        data = {}
        res_export = self.call("Export", data)
        founder_id = actions.get_parameter_value(self.url, 'founder_account', self.token)
        export_app_data = db.get_export_app_data(self.db, appID, founder_id)
        json_app = str(export_app_data, encoding='utf-8')
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'w', encoding='UTF-8') as f:
            data = f.write(json_app)
        if os.path.exists(path):
            file_exist = True
        else:
            file_exist = False
        must_be = dict(resultExport=True,
                      resultFile=True)
        actual = dict(resultExport=int(res_export["blockid"]) > 0,
                      resultFile=file_exist)
        self.unit.assertDictEqual(must_be, actual, "test_Export is failed!")

    def test_ei3_ImportUpload(self):
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        resp = actions.call_contract(self.url, self.pr_key, "ImportUpload",
                                     {'input_file': {'Path': path}}, self.token)
        res_import_upload = self.assert_tx_in_block(resp, self.token)
        self.unit.assertGreater(res_import_upload["blockid"], 0,
                           "BlockId is not generated: " + str(res_import_upload))

    def test_ei4_Import(self):
        founder_id = actions.get_parameter_value(self.url, 'founder_account', self.token)
        import_app_data = db.get_import_app_data(self.db, founder_id)
        import_app_data = import_app_data['data']
        contract_name = "Import"
        data = [{"contract": contract_name,
                 "params": import_app_data[i]} for i in range(len(import_app_data))]
        self.callMulti(contract_name, data, 60)