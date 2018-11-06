import unittest
import json
import os
import time

from libs import actions, tools, db, contract, check


class TestSystemContracts():
    config = tools.read_config("nodes")
    url = config[0]["url"]
    db = config[0]["db"]
    wait = tools.read_config("test")["wait_tx_status"]
    pr_key = config[0]['private_key']
    data = actions.login(url, pr_key, 0)
    token = data["jwtToken"]
    keys = tools.read_fixtures("keys")


    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()


    def assert_tx_in_block(self, result, jwt_token):
        status = actions.tx_status(self.url, self.wait, result, jwt_token)
        if status['blockid'] > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return {"blockid": int(status["blockid"]), "error": "0"}
        else:
            return {"blockid": 0, "error": status["error"]}


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
            #check.is_tx_in_block(status)


    def callMulti(self, name, data, sleep):
        resp = actions.call_multi_contract(self.url, self.pr_key, name, data, self.token)
        time.sleep(sleep)
        resp = self.assert_multi_tx_in_block(resp, self.token)
        return resp


    def wait_block_id(self, old_block_id, limit):
        while True:
            # add contract, which get block_id
            body = "{\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
            tx = contract.new_contract(self.url, self.pr_key, self.token, source=body)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
            currrent_block_id = res["blockid"]
            expected_block_id = old_block_id + limit + 1  # +1 spare block
            if currrent_block_id == expected_block_id:
                break

    def test_create_ecosystem(self):
        tx = contract.new_ecosystem(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_edit_application(self):
        tx = contract.new_application(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, tx['name'], "applications", self.token)
        tx = contract.edit_application(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_activate_application(self):
        tx = contract.new_application(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, tx['name'], "applications", self.token)
        tx_del0 = contract.del_application(self.url, self.pr_key, self.token, id, 0)
        check.is_tx_in_block(self.url, self.wait, tx_del0, self.token)
        tx_del1 = contract.del_application(self.url, self.pr_key, self.token, id, 1)
        check.is_tx_in_block(self.url, self.wait, tx_del1, self.token)

    def test_edit_ecosystem_name(self):
        tx = contract.edit_ecosystem_name(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_edit_ecosystem_name_incorrect_id(self):
        id = 500
        tx = contract.edit_ecosystem_name(self.url, self.pr_key, self.token, id=id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "The ecosystem {id} is not exist".format(id=id)
        self.unit.assertEqual(msg, status["error"], "Is not equals")

    def test_tokens_send(self):
        ldata = actions.login(self.url, self.keys["key2"])
        time.sleep(10)
        sum = "1000"
        tx = contract.tokens_send(self.url, self.pr_key, self.token, ldata['address'], sum)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        is_commission_in_history = actions.is_commission_in_history(
            self.url, self.token,
            self.config[0]["keyID"],
            ldata['key_id'], sum
        )
        self.unit.assertTrue(is_commission_in_history, "No TokensSend resord in history")

    def test_tokens_send_incorrect_wallet(self):
        wallet = "0005-2070-2000-0006"
        msg = "The recipient {wallet} is not valid".format(wallet=wallet)
        tx = contract.tokens_send(self.url, self.pr_key, self.token, wallet, "1000")
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        self.unit.assertEqual(status["error"], msg, "Incorrect message" + msg)

    def test_tokens_send_zero_amount(self):
        ldata = actions.login(self.url, self.keys["key2"], 0)
        tx = contract.tokens_send(self.url, self.pr_key, self.token, ldata['address'], "0")
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Amount equals zero'
        self.unit.assertEqual(status["error"], msg, "Incorrect message" + str(ans))

    def test_tokens_send_negative_amount(self):
        ldata = actions.login(self.url, self.keys["key2"], 0)
        msg = "Amount is less than zero"
        tx = contract.tokens_send(self.url, self.pr_key, self.token, ldata['address'], "-1000")
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        self.unit.assertEqual(status["error"], msg, "Incorrect message" + msg)

    def test_tokens_send_amount_as_string(self):
        ldata = actions.login(self.url, self.keys["key2"], 0)
        msg = "Invalid param 'Amount': can't convert {amount} to decimal".format(amount=amount)
        tx = contract.tokens_send(self.url, self.pr_key, self.token, ldata['address'], "tttt")
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        self.unit.assertEqual(ans["error"], msg, "Incorrect message" + msg)

    def test_new_contract(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_new_contract_exists_name(self):
        tx1 = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx1, self.token)
        tx2 = contract.new_contract(self.url, self.pr_key, self.token, name=tx1["name"])
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "Contract " + cont_name + " already exists"
        self.unit.assertEqual(status["error"], msg, "Incorrect message: " + str(status2))

    def test_new_contract_without_name(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token, name='  ')
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "The contract name is missing"
        self.unit.assertEqual(status["error"], msg, "Incorrect message: " + str(status))

    def test_new_contract_incorrect_condition(self):
        cond = 'condition'
        tx = contract.new_contract(self.url, self.pr_key, self.token, condition=cond)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=cond)
        self.unit.assertIn(msg,  status["error"], "Incorrect message: " + str(status))

    def test_edit_contract_incorrect_condition(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        cond = "tryam"
        id = actions.get_contract_id(self.url, tx['name'], self.token)
        tx2 = contract.edit_contract(self.url, self.pr_key, self.token,
                                     id, new_source=tx['code'], condition=cond)
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "Condition {cond} is not allowed".format(cond=cond)
        self.unit.assertIn(msg, status["error"], "Incorrect message: " + str(ans))

    def test_edit_contract(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_contract_id(self.url, tx['name'], self.token)
        tx2 = contract.edit_contract(self.url, self.pr_key, self.token,
                                     id, new_source=tx['code'], condition="false")
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)

    def test_edit_name_of_contract(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        code1, name1 = tools.generate_name_and_code("")
        id = actions.get_contract_id(self.url, tx['name'], self.token)
        tx2 = contract.edit_contract(self.url, self.pr_key, self.token,
                                     id, new_source=code1)
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "Contracts or functions names cannot be changed"
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_contract(self):
        id = "9999"
        tx2 = contract.edit_contract(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "Item {id} has not been found".format(id=id)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_bind_wallet(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        check.is_tx_in_block(status)
        id = actions.get_contract_id(self.url, name, self.token)
        tx = contract.bind_wallet(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_bind_wallet_incorrect_contract(self):
        id = "99999"
        tx = contract.bind_wallet(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Contract {id} does not exist".format(id=id)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_bind_wallet_incorrect_wallet(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_contract_id(self.url, name, self.token)
        wallet = "0005-2070-2000-0006-0200"
        tx = contract.bind_wallet(self.url, self.pr_key, self.token, id, wallet = wallet)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'The key ID is not found'
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(res))

    def test_unbind_wallet(self):
        tx = contract.new_contract(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_contract_id(self.url, name, self.token)
        tx = contract.bind_wallet(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx = contract.unbind_wallet(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_unbind_wallet_incorrect_wallet(self):
        id = "99999"
        tx = contract.unbind_wallet(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Contract {id} does not exist'.format(id=id)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_new_parameter(self):
        tx = contract.new_parameter(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_new_parameter_exist_name(self):
        tx = contract.new_parameter(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_parameter(self.url, self.pr_key, self.token, name=tx["name"])
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "The parameter {name} is already exist".format(name=tx["name"])
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_new_parameter_incorrect_condition(self):
        condition = "tryam"
        tx = contract.new_parameter(self.url, self.pr_key, self.token, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_edit_incorrect_parameter(self):
        id = "99999"
        tx = contract.edit_parameter(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Item {id} has not been found".format(id=id)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(ans))

    def test_edit_parameter_incorrect_condition(self):
        tx = contract.new_parameter(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_parameter_id(self.url, name, self.token)
        condition = "tryam"
        tx = contract.edit_parameter(self.url, self.pr_key, self.token,
                                     id, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_menu(self):
        tx = contract.new_menu(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        content = {'tree': [{'tag': 'text', 'text': 'Item1'}]}
        m_content = actions.get_content(self.url, "menu", name, "", 1, self.token)
        self.unit.assertEqual(m_content, content)

    def test_new_menu_exist_name(self):
        tx = contract.new_menu(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx = contract.new_menu(self.url, self.pr_key, self.token, name=tx["name"])
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "The menu {name} is already exist".format(name=tx["name"])
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(status))

    def test_new_menu_incorrect_condition(self):
        condition = "tryam"
        tx = contract.new_menu(self.url, self.pr_key, self.token, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_edit_menu(self):
        tx = contract.new_menu(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, tx['name'], "menu", self.token)
        tx2 = contract.edit_menu(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        content = {'tree': [{'tag': 'text', 'text': 'ItemEdited'}]}
        m_content = actions.get_content(self.url, "menu", name, "", 1, self.token)
        self.unit.assertEqual(m_content, content)

    def test_edit_incorrect_menu(self):
        id = "99999"
        tx = contract.edit_menu(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "The item is not found"
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_edit_menu_incorrect_condition(self):
        condition = "tryam"
        tx = contract.new_menu(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, tx['name'], "menu", self.token)
        tx2 = contract.edit_menu(self.url, self.pr_key, self.token, id, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = 'Condition {condition} is not allowed'.format(condition=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_append_menu(self):
        tx = contract.new_menu(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, name, "menu", self.token)
        tx = contract.append_item(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_append_incorrect_menu(self):
        id = "999"
        tx = contract.append_item(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Item {id} has not been found".format(id=id)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_page(self):
        tx = contract.new_page(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        content = [{'tag': 'text', 'text': 'Hello page!'}]
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(cont['tree'], content)

    def test_new_page_exist_name(self):
        tx = contract.new_page(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_page(self.url, self.pr_key, self.token, name=tx["name"])
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "The page {name} is already exist".format(name=tx["name"])
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_page_incorrect_condition(self):
        tx = contract.new_page(self.url, self.pr_key, self.token, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_edit_page(self):
        tx = contract.new_page(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, name, "pages", self.token)
        tx2 = contract.edit_page(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        p_content = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(p_content['tree'], content)

    def test_edit_page_with_validate_count(self):
        tx = contract.new_page(self.url, self.pr_key, self.token, validate_count=6)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        count = actions.get_object_id(self.url, name, "pages", self.token)
        tx2 = contract.edit_page(self.url, self.pr_key, self.token, id, validate_count=1)
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        content = [{'tag': 'text', 'text': 'Good by page!'}]
        p_content = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(p_content['tree'], content)

    def test_edit_incorrect_page(self):
        id = "99999"
        tx = contract.edit_page(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'The item is not found'
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_edit_page_incorrect_condition(self):
        tx = contract.new_page(self.url, self.pr_key, self.token, validate_count=6)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        condition = "Tryam"
        id = actions.get_object_id(self.url, name, "pages", self.token)
        tx2 = contract.edit_page(self.url, self.pr_key, self.token, id, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_append_page(self):
        tx = contract.new_page(self.url, self.pr_key, self.token, validate_count=6)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, name, "pages", self.token)
        tx2 = contract.append_page(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        content = [{'tag': 'text', 'text': 'Hello!\r\nGood by!'}]
        p_content = actions.get_content(self.url, "page", name, "", 1, self.token)
        self.unit.assertEqual(p_content['tree'], content)

    def test_append_page_incorrect_id(self):
        id = "9999"
        tx = contract.append_page(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Item {id} has not been found".format(id=id)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_block(self):
        tx = contract.new_block(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_new_block_exist_name(self):
        tx = contract.new_block(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_block(self.url, self.pr_key, self.token, name=tx["name"])
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "The block '{name}' is already exist".format(name=tx["name"])
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_new_block_incorrect_condition(self):
        condition = "tryam"
        tx = contract.new_block(self.url, self.pr_key, self.token, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'Condition {cond} is not allowed'.format(cond=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_edit_block_incorrect_id(self):
        id = "9999"
        tx = contract.edit_block(self.url, self.pr_key, self.token, id)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = 'The item is not found'
        self.unit.assertEqual(msg, ans["error"], "Incorrect message: " + str(ans))

    def test_edit_block(self):
        tx = contract.new_block(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, name, "blocks", self.token)
        tx2 = contract.edit_block(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)

    def test_edit_block_incorrect_condition(self):
        tx = contract.new_block(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_object_id(self.url, name, "blocks", self.token)
        condition = "tryam"
        tx2 = contract.edit_block(self.url, self.pr_key, self.token, id, condition=condition)
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = 'Condition {condition} is not allowed'.format(condition=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table(self):
        # create new table
        tx = contract.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # create new page
        val = "DBFind(" + table_name + ",src)"
        tx_page = contract.new_page(self.url, self.pr_key, self.token, value=val)
        check.is_tx_in_block(self.url, self.wait, tx_page, self.token)
        # test
        content = [{'tag': 'text', 'text': 'Access denied'}]
        cont = actions.get_content(self.url, "page", tx_page["name"], "", 1, self.token)
        self.unit.assertEqual(cont['tree'], content)

    def test_new_table_not_readable(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # create new contract, which added record in table
        code = """{
        data {}    
        conditions {}    
        action {
            DBInsert("%s", {text: "text1", num: "num1"})    
        }
        }""" % table_name
        tx_cont = contract.new_contract(self.url, self.pr_key, self.token, source=code)
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)
        # call contract
        tx_call = actions.call_contract(url, pr_key, tokentx_cont["name"], {})
        check.is_tx_in_block(self.url, self.wait, {"hash": tx_call}, self.token)
        # create new page
        val = "DBFind(" + table_name + ",src)"
        tx_page = contract.new_page(self.url, self.pr_key, self.token, value=val)
        check.is_tx_in_block(self.url, self.wait, tx_page, self.token)
        # test
        content = [['num1', '1']]
        cont = actions.get_content(self.url, "page", tx_page["name"], "", 1, self.token)
        self.unit.assertEqual(cont['tree'][0]['attr']['data'], content)

    def test_new_table_not_readable_all_columns(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "false"}}
        ]"""
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # create new page
        val = "DBFind(" + table_name + ",src)"
        tx_page = contract.new_page(self.url, self.pr_key, self.token, value=val)
        check.is_tx_in_block(self.url, self.wait, tx_page, self.token)
        # test
        content = [{'tag': 'text', 'text': 'Access denied'}]
        cont = actions.get_content(self.url, "page", tx_page["name"], "", 1, self.token)
        self.unit.assertEqual(cont['tree'], content)

    def test_new_table_not_readable_one_column(self):
        # create new table
        column = """[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update":"true", "read": "false"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]"""
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # create new contract, which added record in table
        code = """{
        data {}    
        conditions {}    
        action {
            DBInsert("%s", {text: "text1", num: "num1"})    
        }
        }""" % table_name
        tx_cont = contract.new_contract(self.url, self.pr_key, self.token, source=code)
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)
        # call contract
        tx_call = actions.call_contract(url, pr_key, tokentx_cont["name"], {})
        check.is_tx_in_block(self.url, self.wait, {"hash": tx_call}, self.token)
        # create new page
        val = "DBFind(" + table_name + ",src)"
        tx_page = contract.new_page(self.url, self.pr_key, self.token, value=val)
        check.is_tx_in_block(self.url, self.wait, tx_page, self.token)
        # test
        content = [['num1', '1']]
        cont = actions.get_content(self.url, "page", tx_page["name"], "", 1, self.token)
        self.unit.assertEqual(cont['tree'][0]['attr']['data'], content)

    def test_new_table_incorrect_column_name_digit(self):
        column = """[{"name":"123","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Column name cannot begin with digit"
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_incorrect_column_name_cyrillic(self):
        word = "привет"
        column = """[{"name":"%s","type":"varchar",
        "index": "1",  "conditions":"true"}]""" % word
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Name {word} must only contain latin, digit and '_', '-' characters".format(word=word)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_incorrect_condition1(self):
        condition = "tryam"
        permissions = "{\"insert\": \"" + condition + \
                      "\", \"update\" : \"true\", \"new_column\": \"true\"}"
        tx = contract.new_table(self.url, self.pr_key, self.token, perms=permissions)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Condition {condition} is not allowed".format(condition=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_incorrect_condition2(self):
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"" + \
                      condition + "\", \"new_column\": \"true\"}"
        tx = contract.new_table(self.url, self.pr_key, self.token, perms=permissions)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Condition {condition} is not allowed".format(condition=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_incorrect_condition3(self):
        condition = "tryam"
        permissions = "{\"insert\": \"true\", \"update\" : \"true\"," + \
                      " \"new_column\": \"" + condition + "\"}"
        tx = contract.new_table(self.url, self.pr_key, self.token, perms=permissions)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Condition {condition} is not allowed".format(condition=condition)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_exist_name(self):
        tx = contract.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)
        tx2 = contract.new_table(self.url, self.pr_key, self.token, name=tx["name"])
        status = actions.tx_status(self.url, self.wait, tx2['hash'], self.token)
        msg = "table {name} exists".format(name=name)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_incorrect_name_cyrillic(self):
        name = "таблица"
        tx = contract.new_table(self.url, self.pr_key, self.token, name=name)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "Name {name} must only contain latin, digit and '_', '-' characters".format(name=name)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))

    def test_new_table_identical_columns(self):
        columns = "[{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}," + \
                  "{\"name\":\"MyName\",\"type\":\"varchar\"," + \
                  "\"index\": \"1\",  \"conditions\":\"true\"}]"
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        self.unit.assertEqual("There are the same columns", status["error"],
                         "Incorrect message: " + str(status))

    def test_edit_table(self):
        tx = contract.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_table(self.url, self.pr_key, self.token, tx["name"])
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)

    def test_new_column(self):
        tx = contract.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="varchar")
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        tx3 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="json")
        check.is_tx_in_block(self.url, self.wait, tx3, self.token)
        tx4 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="number")
        check.is_tx_in_block(self.url, self.wait, tx4, self.token)
        tx5 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="datetime")
        check.is_tx_in_block(self.url, self.wait, tx5, self.token)
        tx6 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="money")
        check.is_tx_in_block(self.url, self.wait, tx6, self.token)
        tx7 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="text")
        check.is_tx_in_block(self.url, self.wait, tx7, self.token)
        tx8 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="double")
        check.is_tx_in_block(self.url, self.wait, tx8, self.token)
        tx9 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx["name"], type="character")
        check.is_tx_in_block(self.url, self.wait, tx9, self.token)

    def test_edit_column(self):
        tx = contract.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_column(self.url, self.pr_key, self.token, tx["name"])
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        tx3 = contract.edit_column(self.url, self.pr_key, self.token,
                                   tx["name"], tx2["name"])
        check.is_tx_in_block(self.url, self.wait, tx3, self.token)

    def test_new_lang(self):
        tx = contract.new_lang(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_new_lang_joint(self):
        tx = contract.new_lang_joint(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_edit_lang_joint(self):
        tx = contract.new_lang_joint(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_count(self.url, "languages", self.token)
        tx2 = contract.edit_lang_joint(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)

    def test_edit_lang(self):
        tx = contract.new_lang(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        id = actions.get_count(self.url, "languages", self.token)
        tx2 = contract.edit_lang(self.url, self.pr_key, self.token, id)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_new_app_param(self):
        tx = contract.new_app_param(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)

    def test_edit_app_param(self):
        tx = contract.new_app_param(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.edit_app_param(self.url, self.pr_key, self.token, 1)
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)

    def test_delayed_contracts(self):
        # add table for test
        column = """[{"name":"id_block","type":"number", "index": "1",  "conditions":"true"}]"""
        tx = contract.new_table(self.url, self.pr_key, self.token, columns=column)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # add contract which insert records in table in progress CallDelayedContract
        body = """
        {
            data{}
            conditions{}
            action {
                DBInsert("%s", {id_block: $block})
            }
        }
        """ % tx["name"]
        tx_cont = contract.new_contract(self.url, self.pr_key, self.token, source=body)
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)
        # NewDelayedContract
        new_limit = 3
        tx2 = contract.new_delayed_contract(self.url, self.pr_key, self.token)
        old_block_id = check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        # get record id of 'delayed_contracts' table for run EditDelayedContract
        id = actions.get_count(self.url, 'delayed_contracts', self.token)
        # wait block_id until run CallDelayedContract
        self.wait_block_id(old_block_id, new_limit)
        # EditDelayedContract
        editLimit = 2
        tx3 = contract.edit_delayed_contract(self.url, self.pr_key, self.token, id,
                                             tx2["name"], limit=editLimit)
        old_block_id = check.is_tx_in_block(self.url, self.wait, tx3, self.token)
        # wait block_id until run CallDelayedContract
        self.wait_block_id(old_block_id, editLimit)
        # verify records count in table
        count = actions.get_count(self.url, tx3["name"], self.token)
        self.unit.assertEqual(int(count), new_limit + editLimit)

    def test_upload_binary(self):
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        tx = contract.upload_binary(self.url, self.pr_key, self.token, path)
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)

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
        tx = contract.new_contract(self.url, self.pr_key, self.token,
                                        name=contract_name, source=body)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
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
        tx = contract.new_contract(self.url, self.pr_key, self.token,
                                        name=contract_name, source=body)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
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
        tx = contract.new_contract(self.url, self.pr_key, self.token,
                                        name=contract_name, source=body)
        status = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        msg = "The contract can't call itself recursively"
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))


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
        tx = contract.new_contract(self.url, self.pr_key, self.token,
                                        name=contract_name, source=body)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        res = actions.call_contract(self.url, self.pr_key, contract_name, {}, self.token)
        status = actions.tx_status(self.url, self.wait, res, self.token)
        msg = "There is loop in @1{con} contract".format(con=contract_name)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))


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
        tx = contract.new_contract(self.url, self.pr_key, self.token,
                                        name=contract_name, source=body)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # test
        msg = "max call depth"
        tx_call = actions.call_contract(self.url, self.pr_key, tx["name"], {}, self.token)
        status = actions.tx_status(self.url, self.wait, tx_call, self.token)
        self.unit.assertEqual(msg, status["error"], "Incorrect message: " + str(status))


    def test_ImportExport(self):
        # Import
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        tx = contract.import_upload(self.url, self.pr_key, self.token, path)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        founder_id = actions.get_parameter_value(self.url, 'founder_account', self.token)
        import_app_data = db.get_import_app_data(self.db, founder_id)
        import_app_data = import_app_data['data']
        contract_name = "Import"
        data = [{"contract": contract_name,
                 "params": import_app_data[i]} for i in range(len(import_app_data))]
        self.callMulti(contract_name, data, 60)
        # Export
        tx_ex = contract.export_new_app(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_ex, self.token)
        data = {}
        res_export = self.call("Export", data)
        founder_id = actions.get_parameter_value(self.url, 'founder_account', self.token)
        export_app_data = actions.get_export_app_data(self.url, self.token, appID, founder_id)
        path = os.path.join(os.getcwd(), "fixtures", "exportApp1.json")
        with open(path, 'w', encoding='UTF-8') as f:
            f.write(export_app_data)
        if os.path.exists(path):
            file_exist = True
        else:
            file_exist = False
        must_be = dict(resultExport=True,
                      resultFile=True)
        actual = dict(resultExport=int(res_export["blockid"]) > 0,
                      resultFile=file_exist)
        self.unit.assertDictEqual(must_be, actual, "test_Export is failed!")


