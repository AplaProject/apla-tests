import unittest
import json
import os
import time

from conftest import setup_vars
from libs import actions
from libs import tools


class TestSystemContracts(unittest.TestCase):

    @classmethod
    def setup_class(self):
        global token
        self.data = actions.login(setup_vars["url1"], setup_vars["private_key"], 0)
        token = self.data["jwtToken"]

    def assert_tx_in_block(self, result, jwtToken, setup_vars):
        self.assertIn("hash", result)
        hash = result['hash']
        status = actions.tx_status(setup_vars["url1"], setup_vars["wait"], hash, jwtToken)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return {"blockid": int(status["blockid"]), "error": "0"}
        else:
            return {"blockid": 0, "error": status["errmsg"]["error"]}

    def call(self, name, data, setup_vars):
        resp = actions.call_contract(setup_vars["url1"], setup_vars["private_key"], name, data, token)
        resp = self.assert_tx_in_block(resp, token, setup_vars())
        return resp

    def assert_multi_tx_in_block(self, result, jwtToken, setup_vars):
        self.assertIn("hashes", result)
        hashes = result['hashes']
        result = actions.tx_status_multi(setup_vars["url1"], setup_vars["wait"], hashes, jwtToken)
        for status in result.values():
            self.assertNotIn('errmsg', status)
            self.assertGreater(int(status["blockid"]), 0,
                               "BlockID not generated")

    def callMulti(self, name, data, sleep, setup_vars):
        resp = actions.call_multi_contract(setup_vars["url1"], setup_vars["private_key"], name, data, token)
        time.sleep(sleep)
        resp = self.assert_multi_tx_in_block(resp, token, setup_vars())
        return resp

    def wait_block_id(self, old_block_id, limit):
        while True:
            # add contract, which get block_id
            body = "{\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
            code, name = tools.generate_name_and_code(body)
            data = {"Value": code, "ApplicationId": 1,
                    "Conditions": "true"}
            res = self.call("NewContract", data, setup_vars())
            self.assertGreater(res["blockid"], 0, "BlockId is not generated: " + str(res))
            currrent_block_id = res["blockid"]
            expected_block_id = old_block_id + limit + 1  # +1 spare block
            if currrent_block_id == expected_block_id:
                break

    def test_create_ecosystem(self):
        data = {"Name": "Ecosys_" + tools.generate_random_name()}
        res = self.call("NewEcosystem", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # !!!
    def test_edit_application(self, setup_vars):
        name = "App" + tools.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_object_id(setup_vars["url1"], name, "applications", token)
        data = {"ApplicationId": id, "Conditions": "false"}
        res = self.call("EditApplication", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_activate_application(self, setup_vars):
        name = "App" + tools.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_object_id(setup_vars["url1"], name, "applications", token)
        dataDeact = {"ApplicationId": id, "Value": 0}
        res = self.call("DelApplication", dataDeact, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataAct = {"ApplicationId": id, "Value": 1}
        res = self.call("DelApplication", dataAct, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_export_application(self, setup_vars):
        name = "App" + tools.generate_random_name()
        data = {"Name": name, "Conditions": "true"}
        res = self.call("NewApplication", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_object_id(setup_vars["url1"], name, "applications", token)
        dataDeact = {"ApplicationId": id}
        res = self.call("ExportNewApp", dataDeact, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # !!!
    def test_edit_ecosystem_name(self):
        id = 1
        data = {"EcosystemID": id, "NewName": "Ecosys_" + tools.generate_random_name()}
        resBlockId = self.call("EditEcosystemName", data, setup_vars())
        self.assertGreater(resBlockId["blockid"], 0,
                           "BlockId is not generated: " + str(resBlockId))

    def test_edit_ecosystem_name_incorrect_id(self):
        id = 500
        data = {"EcosystemID": id, "NewName": "ecosys_" + tools.generate_random_name()}
        res = self.call("EditEcosystemName", data, setup_vars())
        self.assertEqual("Ecosystem " + str(id) + " does not exist", res["error"])

    def test_money_transfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "1000"}
        res = self.call("MoneyTransfer", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))


    def test_money_transfer_incorrect_wallet(self):
        wallet = "0005-2070-2000-0006"
        msg = "Recipient " + wallet + " is invalid"
        data = {"Recipient": wallet, "Amount": "1000"}
        ans = self.call("MoneyTransfer", data, setup_vars())
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_zero_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "0"}
        ans = self.call("MoneyTransfer", data, setup_vars())
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_negative_amount(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "Amount must be greater then zero"
        data = {"Recipient": wallet, "Amount": "-1000"}
        ans = self.call("MoneyTransfer", data, setup_vars())
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_amount_as_string(self):
        wallet = "0005-2070-2000-0006-0200"
        msg = "can't convert ttt to decimal"
        data = {"Recipient": wallet, "Amount": "ttt"}
        ans = self.call("MoneyTransfer", data, setup_vars())
        self.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_money_transfer_with_comment(self):
        wallet = "0005-2070-2000-0006-0200"
        data = {"Recipient": wallet, "Amount": "1000", "Comment": "Test"}
        res = self.call("MoneyTransfer", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_contract(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_contract_exists_name(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewContract", data, setup_vars())
        msg = "Contract " + name + " already exists"
        self.assertEqual(ans["error"], msg, "Incorrect message: " + str(ans))

    def test_new_contract_without_name(self):
        code = "contract {data { }    conditions {    }    action {    }    }"
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        ans = self.call("NewContract", data, setup_vars())
        self.assertIn("must be the name", ans["error"],
                      "Incorrect message: " + str(ans))

    def test_new_contract_incorrect_condition(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "condition"}
        ans = self.call("NewContract", data, setup_vars())
        self.assertEqual("unknown identifier condition",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract_incorrect_condition(self, setup_vars):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": actions.get_contract_id(setup_vars["url1"], name, token),
                 "Value": code, "Conditions": "tryam",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2, setup_vars())
        self.assertEqual("unknown identifier tryam",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract_incorrect_condition1(self, setup_vars):
        wallet = "0005"
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": actions.get_contract_id(setup_vars["url1"], name, token),
                 "Value": code, "Conditions": "true",
                 "WalletId": wallet}
        ans = self.call("EditContract", data2, setup_vars())
        msg = "New contract owner " + wallet + " is invalid"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_contract(self):
        wallet = "0005-2070-2000-0006-0200"  # ??
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_name_of_contract(self, setup_vars):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        code1, name1 = tools.generate_name_and_code("")
        data2 = {"Id": actions.get_contract_id(setup_vars["url1"], name, token),
                 "Value": code1, "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2, setup_vars())
        self.assertEqual("Contracts or functions names cannot be changed",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_contract(self):
        code, name = tools.generate_name_and_code("")
        id = "9999"
        data2 = {"Id": id, "Value": code, "Conditions": "true",
                 "WalletId": "0005-2070-2000-0006-0200"}
        ans = self.call("EditContract", data2, setup_vars())
        self.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_activate_contract(self, setup_vars):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_contract_id(setup_vars["url1"], name, token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_activate_incorrect_contract(self):
        id = "99999"
        data = {"Id": id}
        ans = self.call("ActivateContract", data, setup_vars())
        msg = "Contract " + id + " does not exist"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_deactivate_contract(self, setup_vars):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        id = actions.get_contract_id(setup_vars["url1"], name, token)
        data2 = {"Id": id}
        res = self.call("ActivateContract", data2, setup_vars())
        # self.assertGreater(res["blockid"], 0,        self.conf = self.config.readMainConfig()

    def test_deactivate_incorrect_contract(self):
        id = "99999"
        data = {"Id": id}
        ans = self.call("DeactivateContract", data, setup_vars())
        self.assertEqual("Contract " + id + " does not exist",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_parameter(self):
        data = {"Name": "Par_" + tools.generate_random_name(), "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_parameter_exist_name(self):
        name = "Par_" + tools.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewParameter", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        msg = "Parameter " + name + " already exists"
        ans = self.call("NewParameter", data, setup_vars())
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_parameter_incorrect_condition(self):
        condition = "tryam"
        data = {"Name": "Par_" + tools.generate_random_name(), "Value": "test", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewParameter", data, setup_vars())
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_parameter(self):
        id = "99999"
        data2 = {"Id": id, "Value": "test_edited", "Conditions": "true"}
        ans = self.call("EditParameter", data2, setup_vars())
        self.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_parameter_incorrect_condition(self):
        name = "Par_" + tools.generate_random_name()
        condition = "tryam"
        id = actions.get_parameter_id(setup_vars["url1"], name, token)
        data = {"Name": name, "Value": "test", "Conditions": "true"}
        res = self.call("NewParameter", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": id, "Value": "test_edited", "Conditions": condition}
        ans = self.call("EditParameter", data2, setup_vars())
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_menu(self, setup_vars):
        countMenu = db.get_count_table(setup_vars["db1"], "1_menu")
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        mContent = actions.get_content(setup_vars["url1"], "menu", name, "", 1, token)
        self.assertEqual(mContent, content)

    def test_new_menu_exist_name(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewMenu", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewMenu", data, setup_vars())
        self.assertEqual("Menu " + name + " already exists",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_menu_incorrect_condition(self):
        name = "Menu_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewMenu", data, setup_vars())
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_menu(self, setup_vars):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": "true"}
        res = self.call("EditMenu", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        mContent = actions.get_content(setup_vars["url1"], "menu", name, "", 1, token)
        self.assertEqual(mContent, content)

    def test_edit_incorrect_menu(self):
        id = "99999"
        dataEdit = {"Id": id, "Value": "ItemEdited", "Conditions": "true"}
        ans = self.call("EditMenu", dataEdit, setup_vars())
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_menu_incorrect_condition(self, setup_vars):
        name = "Menu_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "menu", token)
        dataEdit = {"Id": count, "Value": "ItemEdited", "Conditions": condition}
        ans = self.call("EditMenu", dataEdit, setup_vars())
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_append_menu(self, setup_vars):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "Conditions": "true"}
        res = self.call("NewMenu", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "menu", token)
        dataEdit = {"Id": count, "Value": "AppendedItem", "Conditions": "true"}
        res = self.call("AppendMenu", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_append_incorrect_menu(self):
        id = "999"
        dataEdit = {"Id": id, "Value": "AppendedItem", "Conditions": "true"}
        ans = self.call("AppendMenu", dataEdit, setup_vars())
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_page(self, setup_vars):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(cont['tree'], content)

    def test_new_page_exist_name(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewPage", data, setup_vars())
        msg = "Page " + name + " already exists"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_page_incorrect_condition(self):
        name = "Page_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition, "Menu": "default_menu"}
        ans = self.call("NewPage", data, setup_vars())
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_page(self, setup_vars):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"Id": actions.get_count(setup_vars["url1"], "pages", token),
                    "Value": "Good by page!", "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("EditPage", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(pContent['tree'], content)

    def test_edit_page_with_validate_count(self, setup_vars):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "Conditions": "true",
                "ValidateCount": 6, "Menu": "default_menu",
                "ApplicationId": 1}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"Id": actions.get_count(setup_vars["url1"], "pages", token),
                    "Value": "Good by page!", "Conditions": "true",
                    "ValidateCount": 1, "Menu": "default_menu"}
        res = self.call("EditPage", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        pContent = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(pContent['tree'], content)

    def test_edit_incorrect_page(self):
        id = "99999"
        dataEdit = {"Id": id, "Value": "Good by page!",
                    "Conditions": "true", "Menu": "default_menu"}
        ans = self.call("EditPage", dataEdit, setup_vars())
        self.assertEqual("Item " + id + " has not been found",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_edit_page_incorrect_condition(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!",
                "Conditions": "true", "Menu": "default_menu",
                "ApplicationId": 1}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        condition = "Tryam"
        dataEdit = {"Id": actions.get_count(setup_vars["url1"], "pages", token),
                    "Value": "Good by page!", "Conditions": condition,
                    "Menu": "default_menu"}
        ans = self.call("EditPage", dataEdit, setup_vars())
        self.assertEqual("unknown identifier " + condition,
                         ans["error"], "Incorrect message: " + str(ans))

    def test_append_page(self, setup_vars):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello!", "Conditions": "true",
                "Menu": "default_menu", "ApplicationId": 1}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "pages", token)
        dataEdit = {"Id": actions.get_count(setup_vars["url1"], "pages", token),
                    "Value": "Good by!", "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("AppendPage", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        pContent = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(pContent['tree'], content)

    def test_append_page_incorrect_id(self):
        id = "9999"
        dataEdit = {"Id": id, "Value": "Good by!", "Conditions": "true",
                    "Menu": "default_menu"}
        ans = self.call("AppendPage", dataEdit, setup_vars())
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_block(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_block_exist_name(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewBlock", data, setup_vars())
        self.assertEqual("Block " + name + " already exists",
                         ans["error"], "Incorrect message: " + str(ans))

    def test_new_block_incorrect_condition(self):
        name = "Block_" + tools.generate_random_name()
        condition = "tryam"
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": condition}
        ans = self.call("NewBlock", data, setup_vars())
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block_incorrect_id(self, setup_vars):
        id = "9999"
        dataEdit = {"Id": id, "Value": "Good by!", "Conditions": "true"}
        ans = self.call("EditBlock", dataEdit, setup_vars())
        msg = "Item " + id + " has not been found"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "blocks", token)
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": "true"}
        res = self.call("EditBlock", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_block_incorrect_condition(self, setup_vars):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello block!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "blocks", token)
        condition = "tryam"
        dataEdit = {"Id": count, "Value": "Good by!", "Conditions": condition}
        ans = self.call("EditBlock", dataEdit, setup_vars())
        msg = "unknown identifier " + condition
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "true"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        permission = """
        {"read" : "false", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        tableName = "tab_" + tools.generate_random_name()
        data = {"Name": tableName,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + tableName + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [{'tag': 'text', 'text': 'Access denied'}]
        cont = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(cont['tree'], content)

    def test_new_table_not_readable(self, setup_vars):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        permission = """
        {"read" : "true", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        tableName = "tab_" + tools.generate_random_name()
        data = {"Name": tableName,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new contract, which added record in table
        code = """{
        data {}    
        conditions {}    
        action {
            DBInsert("%s", {text: "text1", num: "num1"})    
        }
        }""" % tableName
        code, name = tools.generate_name_and_code(code)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # call contract
        res = self.call(name, "", setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + tableName + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [['num1', '1']]
        cont = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(cont['tree'][0]['attr']['data'], content)

    def test_new_table_not_readable_all_columns(self, setup_vars):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "false"}}
        ]"""
        permission = """
        {"read" : "true", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        tableName = "tab_" + tools.generate_random_name()
        data = {"Name": tableName,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + tableName + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [{'tag': 'text', 'text': 'Access denied'}]
        cont = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(cont['tree'], content)

    def test_new_table_not_readable_one_column(self, setup_vars):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        permission = """
        {"read" : "true", "insert": "true", "update" : "true",  "new_column": "true"}
        """
        tableName = "tab_" + tools.generate_random_name()
        data = {"Name": tableName,
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(int(res["blockid"]), 0, "BlockId is not generated: " + str(res))
        # create new contract, which added record in table
        code = """{
        data {}    
        conditions {}    
        action {
            DBInsert("%s", {text: "text1", num: "num1"})    
        }
        }""" % tableName
        code, name = tools.generate_name_and_code(code)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # call contract
        res = self.call(name, "", setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # create new page
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "DBFind(" + tableName + ",src)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        content = [['num1', '1']]
        cont = actions.get_content(setup_vars["url1"], "page", name, "", 1, token)
        self.assertEqual(cont['tree'][0]['attr']['data'], content)

    def test_new_table_joint(self):
        columns = ["varchar", "Myb", "MyD", "MyM", "MyT", "MyDouble", "MyC"]
        types = ["varchar", "json", "datetime", "money", "text", "double", "character"]
        dicColumns = {"ColumnsArr[]": len(columns), "ColumnsArr[0]": columns[0],
                      "ColumnsArr[1]": columns[1], "ColumnsArr[2]": columns[2],
                      "ColumnsArr[3]": columns[3], "ColumnsArr[4]": columns[4],
                      "ColumnsArr[5]": columns[5], "ColumnsArr[6]": columns[6]}
        dicTypes = {"TypesArr[]": len(types), "TypesArr[0]": types[0],
                    "TypesArr[1]": types[1], "TypesArr[2]": types[2],
                    "TypesArr[3]": types[3], "TypesArr[4]": types[4],
                    "TypesArr[5]": types[5], "TypesArr[6]": types[6]}
        permission = """{"insert": "false", "update" : "true","new_column": "true"}"""
        data = {"ApplicationId": 1,
                "Name": "Tab_" + tools.generate_random_name(),
                "ColumnsArr": dicColumns,
                "TypesArr": dicTypes,
                "InsertPerm": "true",
                "UpdatePerm": "true",
                "ReadPerm": "true",
                "NewColumnPerm": "true"}
        data.update(dicColumns)
        data.update(dicTypes)
        res = self.call("NewTableJoint", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_table_incorrect_column_name_digit(self):
        column = """[{"name":"123","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        ans = self.call("NewTable", data, setup_vars())
        msg = "Column name cannot begin with digit"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_column_name_cyrillic(self):
        word = "привет"
        column = """[{"name":"%s","type":"varchar",
        "index": "1",  "conditions":"true"}]""" % word
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        ans = self.call("NewTable", data, setup_vars())
        msg = "Name " + word + " must only contain latin, digit and '_', '-' characters"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition1(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"" + condition + \
                      "\", \"update\" : \"true\", \"new_column\": \"true\"}"
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data, setup_vars())
        msg = "Condition " + condition + " is not allowed"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition2(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"" + \
                      condition + "\", \"new_column\": \"true\"}"
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data, setup_vars())
        msg = "Condition " + condition + " is not allowed"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_condition3(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"true\"," + \
                      " \"new_column\": \"" + condition + "\"}"
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": columns, "Permissions": permissions,
                "ApplicationId": 1}
        ans = self.call("NewTable", data, setup_vars())
        msg = "Condition " + condition + " is not allowed"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_exist_name(self):
        name = "tab_" + tools.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\" : \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        ans = self.call("NewTable", data, setup_vars())
        msg = "table " + name + " exists"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_table_incorrect_name_cyrillic(self):
        name = "таблица"
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\" : \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        ans = self.call("NewTable", data, setup_vars())
        msg = "Name " + name + " must only contain latin, digit and '_', '-' characters"
        self.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

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
        ans = self.call("NewTable", data, setup_vars())
        self.assertEqual("There are the same columns", ans["error"],
                         "Incorrect message: " + str(ans))

    def test_edit_table(self):
        name = "Tab_" + tools.generate_random_name()
        columns = """[{"name": "MyName", "type": "varchar", "index": "1", "conditions": "true"}]"""
        permissions = """{"insert": "false", "update": "true", "new_column": "true"}"""
        data = {"Name": name, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"Name": name,
                    "InsertPerm": "true",
                    "UpdatePerm": "true",
                    "ReadPerm": "true",
                    "NewColumnPerm": "true"}
        res = self.call("EditTable", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_column(self):
        nameTab = "Tab_" + tools.generate_random_name()
        columns = """[{"name": "MyName", "type":"varchar", "index": "1", "conditions": "true"}]"""
        permissions = """{"insert": "false", "update": "true", "new_column": "true"}"""
        data = {"ApplicationId": 1,
                "Name": nameTab,
                "Columns": columns,
                "Permissions": permissions, }
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol1 = {"TableName": nameTab,
                    "Name": "var",
                    "Type": "varchar",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res1 = self.call("NewColumn", dataCol1, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol2 = {"TableName": nameTab,
                    "Name": "json",
                    "Type": "json",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res2 = self.call("NewColumn", dataCol2, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol3 = {"TableName": nameTab,
                    "Name": "num",
                    "Type": "number",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res3 = self.call("NewColumn", dataCol3, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol4 = {"TableName": nameTab,
                    "Name": "date",
                    "Type": "datetime",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res4 = self.call("NewColumn", dataCol4, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol5 = {"TableName": nameTab,
                    "Name": "sum",
                    "Type": "money",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res5 = self.call("NewColumn", dataCol5, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol6 = {"TableName": nameTab,
                    "Name": "name",
                    "Type": "text",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res6 = self.call("NewColumn", dataCol6, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol7 = {"TableName": nameTab,
                    "Name": "length",
                    "Type": "double",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res7 = self.call("NewColumn", dataCol7, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataCol8 = {"TableName": nameTab,
                    "Name": "code",
                    "Type": "character",
                    "UpdatePerm": "true",
                    "ReadPerm": "true"}
        res8 = self.call("NewColumn", dataCol8, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_column(self):
        nameTab = "tab_" + tools.generate_random_name()
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        permissions = "{\"insert\": \"false\", \"update\": \"true\"," + \
                      " \"new_column\": \"true\"}"
        data = {"Name": nameTab, "Columns": columns,
                "Permissions": permissions, "ApplicationId": 1}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        name = "Col_" + tools.generate_random_name()
        dataCol = {"TableName": nameTab, "Name": name, "Type": "number",
                   "UpdatePerm": "true", "ReadPerm": "true"}
        res = self.call("NewColumn", dataCol, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        dataEdit = {"TableName": nameTab, "Name": name, "Type": "number",
                    "UpdatePerm": "false", "ReadPerm": "false"}
        res = self.call("EditColumn", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_lang(self):
        data = {"AppID": 1, "Name": "Lang_" + tools.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
        res = self.call("NewLang", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_lang_joint(self):
        data = {"ApplicationId": 1,
                "Name": "Lang_" + tools.generate_random_name(),
                "ValueArr": ["en", "ru"], "LocaleArr": ["Hi", "Привет"]}
        res = self.call("NewLangJoint", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_lang_joint(self, setup_vars):
        data = {"ApplicationId": 1,
                "Name": "Lang_" + tools.generate_random_name(),
                "ValueArr": ["en", "ru"], "LocaleArr": ["Hi", "Привет"]}
        res = self.call("NewLangJoint", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "languages", token)
        dataE = {"Id": count, "ValueArr": ["en", "de"],
                 "LocaleArr": ["Hi", "Hallo"]}
        res = self.call("EditLangJoint", dataE, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_lang(self, setup_vars):
        name = "Lang_" + tools.generate_random_name()
        data = {"AppID": 1, "Name": name, "ApplicationId": 1,
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("NewLang", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "languages", token)
        dataEdit = {"Id": count, "Name": name, "AppID": 1,
                    "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        res = self.call("EditLang", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _new_sign(self):
        name = "Sign_" + tools.generate_random_name()
        value = "{\"forsign\":\"" + name + \
                "\", \"field\": \"" + name + "\", \"title\": \"" + name + \
                "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value, "Conditions": "true"}
        res = self.call("NewSign", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _new_sign_joint(self):
        name = "Sign_" + tools.generate_random_name()
        params = [{"name": "test", "text": "test"},
                  {"name": "test2", "text": "test2"}]
        values = ["one", "two"]
        data = {"Name": name, "Title": name, "ParamArr": params,
                "ValueArr": values, "Conditions": "true"}
        res = self.call("NewSignJoint", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _edit_sign_joint(self, setup_vars):
        name = "Sign_" + tools.generate_random_name()
        params = [{"name": "test", "text": "test"},
                  {"name": "test2", "text": "test2"}]
        values = ["one", "two"]
        data = {"Name": name, "Title": name, "ParamArr": params,
                "ValueArr": values, "Conditions": "true"}
        res = self.call("NewSignJoint", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "signatures", token)
        dataE = {"Id": count, "Title": "NewTitle", "Parameter": str(params),
                 "Conditions": "true"}
        resE = self.call("EditSignJoint", dataE, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    # off
    def _edit_sign(self):
        name = "Sign_" + tools.generate_random_name()
        value = "{\"forsign\":\"" + name + \
                "\", \"field\": \"" + name + "\", \"title\": \"" + name + \
                "\", \"params\":[{\"name\": \"test\", \"text\": \"test\"}]}"
        data = {"Name": name, "Value": value, "Conditions": "true"}
        res = self.call("NewSign", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        count = actions.get_count(setup_vars["url1"], "signatures", token)
        valueE = "{\"forsign\": \"" + name + "\", \"field\": \"" + \
                 name + "\", \"title\": \"" + name + \
                 "\", \"params\":[{\"name\": \"test1\", \"text\": \"test2\"}]}"
        dataEdit = {"Id": count, "Value": valueE, "Conditions": "true"}
        res = self.call("EditSign", dataEdit, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_new_app_param(self):
        name = "param_" + tools.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true"}
        res = self.call("NewAppParam", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_app_param(self):
        name = "param_" + tools.generate_random_name()
        data = {"ApplicationId": 1, "Name": name, "Value": "myParam", "Conditions": "true"}
        res = self.call("NewAppParam", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        data2 = {"Id": 1, "Name": name, "Value": "myParamEdited", "Conditions": "true"}
        res = self.call("EditAppParam", data2, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_delayed_contracts(self, setup_vars):
        # add table for test
        column = """[{"name":"id_block","type":"number", "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "true", "update" : "true","new_column": "true"}"""
        table_name = "tab_delayed_" + tools.generate_random_name()
        data = {"Name": table_name, "Columns": column,
                "ApplicationId": 1, "Permissions": permission}
        res = self.call("NewTable", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
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
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # NewDelayedContract
        newLimit = 3
        data = {"Contract": contract_name, "EveryBlock": "1",
                "Conditions": "true", "Limit": newLimit}
        res = self.call("NewDelayedContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        old_block_id = int(res["blockid"])
        # get record id of 'delayed_contracts' table for run EditDelayedContract
        res = actions.call_get_api(setup_vars["url1"] + "/list/delayed_contracts", "", token)
        count = len(res["list"])
        id = res["list"][0]["id"]
        i = 1
        while i < count:
            if res["list"][i]["id"] > id:
                id = res["list"][i]["id"]
            i = i + 1
        # wait block_id until run CallDelayedContract
        self.wait_block_id(old_block_id, newLimit)
        # EditDelayedContract
        editLimit = 2
        data = {"Id": id, "Contract": contract_name, "EveryBlock": "1", "Conditions": "true", "Limit": editLimit}
        res = self.call("EditDelayedContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        old_block_id = res["blockid"]
        # wait block_id until run CallDelayedContract
        self.wait_block_id(old_block_id, editLimit)
        # verify records count in table
        count = actions.get_count(setup_vars["url1"], table_name, token)
        self.assertEqual(int(count), newLimit + editLimit)

    def test_upload_binary(self, setup_vars):
        name = "image_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": 1}
        resp = actions.call_contract_with_files(setup_vars["url1"], setup_vars["private_key"], "UploadBinary",
                                                data, files, token)
        res = self.assert_tx_in_block(resp, token, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_update_system_parameters(self):
        data = {"Name": "max_block_user_tx", "Value": "2"}
        res = self.call("UpdateSysParam", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_contract_recursive_call_by_name_action(self):
        contractName = "recur_" + tools.generate_random_name()
        body = """
        {
        data { }
        conditions { }
        action {
            Println("hello1")
            %s()
            }
        }
        """ % contractName
        code = tools.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        msg = "The contract can't call itself recursively"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_by_name_conditions(self):
        contractName = "recur_" + tools.generate_random_name()
        body = """
        {
        data { }
        conditions { 
            Println("hello1")
            %s()
            }
        action { }
        }
        """ % contractName
        code = tools.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        msg = "The contract can't call itself recursively"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_by_name_func_action(self):
        contractName = "recur_" + tools.generate_random_name()
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
        """ % contractName
        code = tools.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        msg = "The contract can't call itself recursively"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_action(self):
        contractName = "recur_" + tools.generate_random_name()
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
        """ % contractName
        code = tools.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        res = self.call(contractName, "", setup_vars())
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_conditions(self):
        contractName = "recur_" + tools.generate_random_name()
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
        """ % contractName
        code = tools.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        res = self.call(contractName, "", setup_vars())
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_contract_recursive_call_contract_func_conditions(self):
        contractName = "recur_" + tools.generate_random_name()
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
        """ % contractName
        code = tools.generate_code(contractName, body)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewContract", data, setup_vars())
        res = self.call(contractName, "", setup_vars())
        msg = "There is loop in @1" + contractName + " contract"
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

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
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        data = ""
        msg = "Memory limit exceeded"
        res = self.call(contract_name, data, setup_vars())
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

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
        res = self.call("NewContract", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        # test
        data = ""
        msg = "max call depth"
        res = self.call(contract_name, data, setup_vars())
        self.assertEqual(msg, res["error"], "Incorrect message: " + str(res))

    def test_ei1_ExportNewApp(self):
        appID = 1
        data = {"ApplicationId": appID}
        res = self.call("ExportNewApp", data, setup_vars())
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_ei2_Export(self, setup_vars):
        appID = 1
        data = {}
        resExport = self.call("Export", data, setup_vars())
        founderID = db.get_founder_id(setup_vars["db1"])
        exportAppData = db.get_export_app_data(setup_vars["db1"], appID, founderID)
        jsonApp = str(exportAppData, encoding='utf-8')
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'w', encoding='UTF-8') as f:
            data = f.write(jsonApp)
        if os.path.exists(path):
            fileExist = True
        else:
            fileExist = False
        mustBe = dict(resultExport=True,
                      resultFile=True)
        actual = dict(resultExport=int(resExport["blockid"]) > 0,
                      resultFile=fileExist)
        self.assertDictEqual(mustBe, actual, "test_Export is failed!")

    def test_ei3_ImportUpload(self, setup_vars):
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'r') as f:
            file = f.read()
        files = {'input_file': file}
        resp = actions.call_contract_with_files(setup_vars["url1"], setup_vars["private_key"], "ImportUpload", {},
                                                files, token)
        resImportUpload = self.assert_tx_in_block(resp, token, setup_vars())
        self.assertGreater(resImportUpload["blockid"], 0,
                           "BlockId is not generated: " + str(resImportUpload))

    def test_ei4_Import(self, setup_vars):
        founderID = db.get_founder_id(setup_vars["db1"])
        importAppData = db.get_import_app_data(setup_vars["db1"], founderID)
        importAppData = importAppData['data']
        contractName = "Import"
        data = [{"contract": contractName,
                 "params": importAppData[i]} for i in range(len(importAppData))]
        self.callMulti(contractName, data, 60, setup_vars())