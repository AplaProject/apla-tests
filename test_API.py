import unittest
import requests
import json
import os
import time

from libs import actions, tools, api

class TestApi():
    config = tools.read_config("nodes")
    url = config[1]["url"]
    wait = tools.read_config("test")["wait_tx_status"]
    pr_key = config[0]['private_key']
    data = actions.login(url, pr_key, 0)
    token = data["jwtToken"]

    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, result, jwt_token):
        status = actions.tx_status(self.url, self.wait, result, jwt_token)
        if status['blockid'] > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, end_point, data, keys):
        end = self.url + end_point
        result = actions.call_get_api(end, data, self.token)
        for key in keys:
            self.unit.assertIn(key, result)
        return result

    def check_post_api(self, end_point, data, keys):
        end = self.url + end_point
        result = actions.call_post_api(end, data, self.token)
        for key in keys:
            self.unit.assertIn(key, result)
        return result


    def get_error_api(self, end_point, data):
        end = self.url + end_point
        result = actions.call_get_api(end, data, self.token)
        print(result)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data):
        resp = actions.call_contract(self.url, self.pr_key, name, data, self.token)
        resp = self.assert_tx_in_block(resp, self.token)
        return resp

    def check_result(self, result, keys, error='', msg=''):
        for key in keys:
            self.unit.assertIn(key, result)
        if 'error' and 'msg' in result:
            expected = dict(
                error=error,
                msg=msg,
            )
            actual = dict(
                error=result['error'],
                msg=result['msg']
            )
            self.unit.assertDictEqual(expected, actual, 'Incorrect error ' + str(result))
        return result



    def test_balance(self):
        asserts = ['amount', 'money']
        res = api.balance(self.url, self.token, self.data['address'])
        self.check_result(res, asserts)


    def test_balance_incorrect_wallet(self):
        wallet = '0000-0990-3244-5453-2310'
        asserts = ['error', 'msg']
        res = api.balance(self.url, self.token, wallet)
        error = 'E_INVALIDWALLET'
        msg = 'Wallet {} is not valid'.format(wallet)
        self.check_result(res, asserts, error, msg)


    def test_get_ecosystem(self):
        asserts = ['number']
        res = api.ecosystems(self.url, self.token)
        self.check_result(res, asserts)


    def test_get_param_current_ecosystem(self):
        asserts = ['list']
        res = api.ecosystemparams(self.url, self.token)
        self.check_result(res, asserts)


    def test_get_params_ecosystem_with_names(self):
        asserts = ['list']
        names = 'founder_account,new_table,changing_tables'
        res = api.ecosystemparams(self.url, self.token, names=names)
        self.check_result(res, asserts)
        must_be = [
            '3',
            'founder_account',
            'new_table',
            'changing_tables',
        ]
        actual = [
            str(len(res['list'])),
            res['list'][0]['name'],
            res['list'][1]['name'],
            res['list'][2]['name'],
        ]
        must_be.sort()
        actual.sort()
        self.unit.assertEqual(actual, must_be, 'test_get_params_ecosystem_with_names is failed!')


    def test_get_parametr_of_current_ecosystem(self):
        asserts = ['id', 'name', 'value', 'conditions']
        param = 'founder_account'
        res = api.ecosystemparam(self.url, self.token, name=param)
        self.check_result(res, asserts)


    def test_get_incorrect_ecosys_parametr(self):
        param = 'incorrectParam'
        asserts = ['error', 'msg']
        res = api.ecosystemparam(self.url, self.token, name=param)
        error = 'E_PARAMNOTFOUND'
        msg = 'Parameter {} has not been found'.format(param)
        self.check_result(res, asserts, error, msg)

    def test_get_tables_of_current_ecosystem(self):
        asserts = ['list', 'count']
        res = api.tables(self.url, self.token)
        self.check_result(res, asserts)

    def test_get_table_information(self):
        dict_names = {}
        dict_names_api = {}
        tables = actions.get_ecosys_tables(self.url, self.token)
        for table in tables:
            if 'table' not in table:
                table_info = api.table(self.url, self.token, table)
                if 'name' in table_info:
                    dict_names[table] = table
                    dict_names_api[table] = table_info['name']
                else:
                    self.unit.fail('Answer from API /table/' + table + ' is: ' + str(table_info))
        self.unit.assertDictEqual(dict_names_api, dict_names,
                             'Any of API tableInfo gives incorrect data')

    def test_get_incorrect_table_information(self):
        table = 'tab'
        asserts = ['error', 'msg']
        res = api.table(self.url, self.token, table)
        error = 'E_TABLENOTFOUND'
        msg = 'Table ' + table + ' has not been found'
        self.check_result(res, asserts, error, msg)


    def test_get_table_data(self):
        asserts = ['count', 'list']
        tables = actions.get_ecosys_tables(self.url, self.token)
        for table in tables:
            table_data = api.list(self.url, self.token, table)
            self.check_result(table_data, asserts)


    def test_get_table_data_row(self):
        asserts = ['value']
        res = api.row(self.url, self.token, 'contracts', 2)
        self.check_result(res, asserts)

    def test_get_incorrect_table_data_row(self):
        table = 'tab'
        row = 2
        asserts = ['error', 'msg']
        res = api.row(self.url, self.token, table, row)
        error = 'E_QUERY'
        msg = 'DB query is wrong'
        self.check_result(res, asserts, error, msg)

    def test_get_contract_information(self):
        asserts = ['id', 'name', 'address']
        res = api.contract(self.url, self.token, 'MainCondition')
        self.check_result(res, asserts)

    def test_get_incorrect_contract_information(self):
        contract = "contract"
        data = {}
        error, message = self.get_error_api("/contract/" + contract, data)
        err = "E_CONTRACT"
        msg = "There is not " + contract + " contract"

    def test_content_lang(self):
        name_lang = "Lang_" + tools.generate_random_name()
        data = {"Name": name_lang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        name_page = "Page_" + tools.generate_random_name()
        value_page = "Hello, LangRes(" + name_lang + ")"
        data_page = {"ApplicationId": 1, "Name": name_page, "Value": value_page, "Conditions": "true",
                    "Menu": "default_menu"}
        res = self.call("NewPage", data_page)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello, World_en'}]
        content_ru = [{'tag': 'text', 'text': 'Hello, Мир_ru'}]
        content_fr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR'}]
        content_de = [{'tag': 'text', 'text': 'Hello, Welt_de'}]
        dict_exp ={"default" : content, "ru": content_ru,
                  "fr": content_fr, "de": content_de, "pe": content}
        p_content = actions.get_content(self.url, "page", name_page, "en", 1, self.token)     # should be: en
        ru_p_content = actions.get_content(self.url, "page", name_page, "ru", 1, self.token)      # should be: ru
        fr_p_content = actions.get_content(self.url, "page", name_page, "fr-FR", 1, self.token) # should be: fr-FR
        de_p_content = actions.get_content(self.url, "page", name_page, "de-DE", 1, self.token)   # should be: de
        pe_p_content = actions.get_content(self.url, "page", name_page, "pe", 1, self.token)      # should be: en
        dict_cur = {"default" : p_content['tree'], "ru": ru_p_content['tree'],
                  "fr": fr_p_content['tree'], "de": de_p_content['tree'], "pe": pe_p_content['tree']}
        self.unit.assertDictEqual(dict_cur, dict_exp, "One of langRes is faild")

    def test_content_lang_after_edit(self):
        name_lang = "Lang_" + tools.generate_random_name()
        data = {"Name": name_lang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = self.call("NewLang", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        name_page = "Page_" + tools.generate_random_name()
        value_page = "Hello, LangRes(" + name_lang + ")"
        data_page = {"Name": name_page, "Value": value_page, "Conditions": "true",
                    "Menu": "default_menu", "ApplicationId": 1,}
        res = self.call("NewPage", data_page)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        count = self.check_get_api("/list/languages", "", [])["count"]
        data_edit = {"Id": count,
                "Trans": "{\"en\": \"World_en_ed\", \"ru\" : \"Мир_ru_ed\"," +\
                "\"fr-FR\": \"Monde_fr-FR_ed\", \"de\": \"Welt_de_ed\"}"}
        res = self.call("EditLang", data_edit)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello, World_en_ed'}]
        content_ru = [{'tag': 'text', 'text': 'Hello, Мир_ru_ed'}]
        content_fr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR_ed'}]
        content_de = [{'tag': 'text', 'text': 'Hello, Welt_de_ed'}]
        dict_exp ={"default" : content, "ru": content_ru,
                  "fr": content_fr, "de": content_de, "pe": content}
        p_content = actions.get_content(self.url, "page", name_page, "en", 1, self.token)          # should be: en
        ru_p_content = actions.get_content(self.url, "page", name_page, "ru", 1, self.token)      # should be: ru
        fr_p_content = actions.get_content(self.url, "page", name_page, "fr-FR", 1, self.token) # should be: fr-FR
        de_p_content = actions.get_content(self.url, "page", name_page, "de-DE", 1, self.token)   # should be: de
        pe_p_content = actions.get_content(self.url, "page", name_page, "pe", 1, self.token)      # should be: en
        dict_cur = {"default" : p_content['tree'], "ru": ru_p_content['tree'],
                  "fr": fr_p_content['tree'], "de": de_p_content['tree'], "pe": pe_p_content['tree']}
        self.unit.assertDictEqual(dict_cur, dict_exp, "One of langRes is faild")

    def test_get_content_from_template(self):
        data = {}
        data["template"] = "SetVar(mytest, 100) Div(Body: #mytest#)"
        asserts = ["tree"]
        res = self.check_post_api("/content", data, asserts)
        answer_tree = {'tree': [{'tag': 'div', 'children': [{'tag': 'text', 'text': '100'}]}]}
        self.unit.assertEqual(answer_tree, res)

    def test_get_content_from_template_source(self):
        data = {}
        data["template"] = "SetVar(mytest, 100) Div(Body: #mytest#)"
        data["source"] = "true"
        asserts = ["tree"]
        res = self.check_post_api("/content", data, asserts)
        answer_tree = {'tree': [{'tag': 'setvar', 'attr': {'name': 'mytest', 'value': '100'}}, {'tag': 'div', 'children': [{'tag': 'text', 'text': '#mytest#'}]}]}
        self.unit.assertEqual(answer_tree, res)

    def test_get_content_source(self):
        # Create new page for test
        name = "Page_" + tools.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "SetVar(a,\"Hello\") \n Div(Body: #a#)"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        asserts = ["tree"]
        res = self.check_post_api("/content/source/"+name, "", asserts)
        childrenText = res["tree"][1]["children"][0]["text"]
        self.unit.assertEqual("#a#", childrenText)

    def test_get_content_with_param_from_address_string(self):
        # Create new page for test
        name = "Page_" + tools.generate_random_name()
        data = {}
        data["Name"] = name
        data["Value"] = "#test#"
        data["Conditions"] = "true"
        data["Menu"] = "default_menu"
        data["ApplicationId"] = 1
        res = self.call("NewPage", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        param = "?test="
        value = "hello123"
        asserts = ["tree"]
        res = self.check_post_api("/content/page/" + name + param + value, "", asserts)
        self.unit.assertEqual(value, res["tree"][0]["text"])

    def test_get_content_from_another_ecosystem(self):
        # create new ecosystem
        ecosys_name = "Ecosys_" + tools.generate_random_name()
        data = {"Name": ecosys_name}
        res = self.call("NewEcosystem", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        ecosys_num = actions.call_get_api(self.url + "/ecosystems/", "", self.token)["number"]
        # login founder in new ecosystem
        data2 = actions.login(self.url, self.pr_key, 0, ecosys_num)
        token2 = data2["jwtToken"]
        # create page in new ecosystem
        page_name = "Page_" + tools.generate_random_name()
        page_text = "Page in "+str(ecosys_num)+" ecosystem"
        page_value = "Span("+page_text+")"
        data = {"Name": page_name, "Value": page_value, 'ApplicationId': 1,
                "Conditions": "true", "Menu": "default_menu"}
        resp = actions.call_contract(self.url, self.pr_key, "@1NewPage",
                                     data, token2, ecosystem=ecosys_num)
        status = actions.tx_status(self.url, self.wait, resp, token2)
        self.unit.assertGreater(status["blockid"], 0,
                                "BlockId is not generated: " + str(status))
        # create menu in new ecosystem
        menu_name = "Menu_" + tools.generate_random_name()
        menu_title = "Test menu"
        data = {"Name": menu_name, "Value": "MenuItem(Title:\""+menu_title+"\")",
                "Conditions": "true"}
        resp = actions.call_contract(self.url, self.pr_key, "@1NewMenu",
                                   data, token2, ecosystem=ecosys_num)
        status = actions.tx_status(self.url, self.wait, resp, token2)
        self.unit.assertGreater(status["blockid"], 0,
                                "BlockId is not generated: " + str(status))
        # test
        data = ""
        asserts = ["tree"]
        res_page = self.check_post_api("/content/page/@" + str(ecosys_num) + page_name,
                                      data, asserts)
        res_menu = self.check_post_api("/content/menu/@" + str(ecosys_num) + menu_name,
                                      data, asserts)
        must_be = dict(page_text=page_text,
                      menu=menu_title)
        expected_value = dict(page_text=res_page["tree"][0]["children"][0]["text"],
                      menu=res_menu["tree"][0]["attr"]["title"])
        self.unit.assertEqual(must_be, expected_value, "Dictionaries are different!")

    def test_get_back_api_version(self):
        asserts = ["."]
        data = ""
        self.check_get_api("/version", data, asserts)

    def test_get_systemparams_all_params(self):
        asserts = ["list"]
        res = self.check_get_api("/systemparams", "", asserts)
        self.unit.assertGreater(len(res["list"]), 0, "Count of systemparams not Greater 0: " + str(len(res["list"])))

    def test_get_systemparams_some_param(self):
        asserts = ["list"]
        param = "gap_between_blocks"
        res = self.check_get_api("/systemparams/?names=" + param, "", asserts)
        self.unit.assertEqual(1, len(res["list"]))
        self.unit.assertEqual(param, res["list"][0]["name"])

    def test_get_systemparams_incorrect_param(self):
        asserts = ["list"]
        param = "not_exist_parameter"
        res = self.check_get_api("/systemparams/?names="+param, "", asserts)
        self.unit.assertEqual(0, len(res["list"]))

    def test_get_contracts(self):
        limit = 25 # Default value without parameters
        asserts = ["list"]
        res = self.check_get_api("/contracts", "", asserts)
        self.unit.assertEqual(limit, len(res["list"]))

    def test_get_contracts_limit(self):
        limit = 3
        asserts = ["list"]
        res = self.check_get_api("/contracts/?limit="+str(limit), "", asserts)
        self.unit.assertEqual(limit, len(res["list"]))

    def test_get_contracts_offset(self):
        asserts = ["list"]
        res = self.check_get_api("/contracts", "", asserts)
        count = res["count"]
        offset = count
        res = self.check_get_api("/contracts/?offset=" + str(offset), "", asserts)
        self.unit.assertEqual(None, res["list"])

    def test_get_contracts_empty(self):
        limit = 1000
        offset = 1000
        asserts = ["list"]
        res = self.check_get_api("/contracts/?limit="+str(limit)+"&offset="+str(offset), "", asserts)
        self.unit.assertEqual(None, res["list"])

    def test_get_interface_page(self):
        asserts = ["id"]
        page = "default_page"
        res = self.check_get_api("/interface/page/"+page, "", asserts)
        self.unit.assertEqual("default_page", res["name"])

    def test_get_interface_page_incorrect(self):
        asserts = ["error"]
        page = "not_exist_page_xxxxxxxxxxx"
        res = self.check_get_api("/interface/page/"+page, "", asserts)
        self.unit.assertEqual("Page not found", res["msg"])

    def test_get_interface_menu(self):
        asserts = ["id"]
        menu = "default_menu"
        res = self.check_get_api("/interface/menu/"+menu, "", asserts)
        self.unit.assertEqual("default_menu", res["name"])

    def test_get_interface_menu_incorrect(self):
        asserts = ["error"]
        menu = "not_exist_menu_xxxxxxxxxxx"
        res = self.check_get_api("/interface/menu/"+menu, "", asserts)
        self.unit.assertEqual("Page not found", res["msg"])

    def test_get_interface_block(self):
        # Add new block
        block = "Block_" + tools.generate_random_name()
        data = {"Name": block, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("NewBlock", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        asserts = ["id"]
        res = self.check_get_api("/interface/block/"+block, "", asserts)
        self.unit.assertEqual(block, res["name"])

    def test_get_interface_block_incorrect(self):
        asserts = ["error"]
        block = "not_exist_block_xxxxxxxxxxx"
        res = self.check_get_api("/interface/block/"+block, "", asserts)
        self.unit.assertEqual("Page not found", res["msg"])

    def test_get_table_vde(self):
        asserts = ["name"]
        data = {"vde": "true"}
        self.check_get_api("/table/contracts", data, asserts)

    def test_create_vde(self):
        asserts = ["result"]
        data = {}
        #self.check_post_api("/vde/create", data, asserts)

    def is_node_owner_true(self):
        data = {}
        resp = actions.call_contract(self.url, self.pr_key, "NodeOwnerCondition", data, self.token)
        status = actions.tx_status(self.url, self.wait, resp, self.token)
        self.unit.assertGreater(int(status["blockid"]), 0,
                           "BlockId is not generated: " + str(status))

    def is_node_owner_false(self):
        keys = tools.read_config("keys")
        pr_key2 = keys["key1"]
        data2 = actions.login(self.url, pr_key2, 0)
        token2 = data2["jwtToken"]
        data = {}
        resp = actions.call_contract(self.url, pr_key2, "NodeOwnerCondition", data, token2)
        status = actions.tx_status(self.url, self.wait, resp, token2)
        self.unit.assertEqual(status["errmsg"]["error"],
                         "Sorry, you do not have access to this action.",
                         "Incorrect message: " + str(status))

    def test_login(self):
        keys = tools.read_fixtures("keys")
        data1 = actions.login(self.url, keys["key5"], 0)
        time.sleep(5)
        conf = tools.read_config("nodes")
        res = actions.is_wallet_created(self.url, self.token, data1["key_id"])
        self.unit.assertTrue(res, "Wallet for new user didn't created")

    def test_login2(self):
        is_one = False
        keys = tools.read_fixtures("keys")
        data1 = actions.login(self.url, keys["key3"], 0)
        time.sleep(5)
        conf = tools.read_config("nodes")
        res = actions.is_wallet_created(self.url, self.token, data1["key_id"])
        if res == True:
            data2 = actions.login(self.url, keys["key1"], 0)
            time.sleep(5)
            is_one = actions.is_wallet_created(self.url, self.token, data2["key_id"])
            self.unit.assertTrue(is_one, "Wallet for new user didn't created")

    def test_get_avatar_with_login(self):
        # add file in binaries
        name = "file_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {"Name": name, "ApplicationId": 1, 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary", data, self.token)
        res = self.assert_tx_in_block(resp, self.token)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        # find last added file
        asserts = ["count"]
        res = self.check_get_api("/list/binaries", "", asserts)
        last_rec = res["count"]
        # find founder ID
        asserts = ["list"]
        res = self.check_get_api("/list/members", "", asserts)
        # iterating response elements
        i = 0
        founder_id = ""
        while i < len(res['list']):
            if res['list'][i]['member_name'] == "founder":
                founder_id = res['list'][i]['id']
            i += 1
        # change column permissions
        data = {'member_name': 'founder',
                'image_id': last_rec}
        res = self.call("ProfileEdit", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        # test
        ecosystem_id = "1"
        asserts = ""
        data = ""
        ava_url = self.url + "/avatar/" + ecosystem_id + "/" + founder_id
        res = actions.call_get_api_with_full_response(ava_url, data, asserts)
        msg = "Content-Length is different!"
        self.unit.assertIn("71926", str(res.headers["Content-Length"]),msg)

    def test_get_avatar_without_login(self):
        # add file in binaries
        name = "file_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {"Name": name, "ApplicationId": 1, "DataMimeType":"image/jpeg", 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary", data, self.token)
        res = self.assert_tx_in_block(resp, self.token)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        # find last added file
        asserts = ["count"]
        res = self.check_get_api("/list/binaries", "", asserts)
        last_rec = res["count"]
        # find founder ID
        asserts = ["list"]
        res = self.check_get_api("/list/members", "", asserts)
        # iterating response elements
        i = 0
        founder_id = ""
        while i < len(res['list']):
            if res['list'][i]['member_name'] == "founder":
                founder_id = res['list'][i]['id']
            i += 1
        # change column permissions
        data = {'member_name': 'founder',
                'image_id': last_rec}
        res = self.call("ProfileEdit", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        # test
        ecosystem_id = "1"
        ava_url = self.url + "/avatar/" + ecosystem_id + "/" + founder_id
        resp = requests.get(ava_url)
        msg = "Content-Length is different!"
        self.unit.assertIn("71926", str(resp.headers["Content-Length"]), msg)

    def test_get_centrifugo_address_without_login(self):
        resp = requests.get(self.url + '/config/centrifugo')
        res = resp.json()
        self.unit.assertIn("ws://", res, "Centrifugo is not connection to node!")

    def test_get_centrifugo_address_with_login(self):
        asserts = ["ws://"]
        data = ""
        res = self.check_get_api("/config/centrifugo", data, asserts)

    def test_content_hash(self):
        # 1. test with login
        # 2. test without login
        # 3. negative test without login
        def is_hash_not_empty(hash):
            hash = str(hash)
            if hash.find("{'hash':") != -1:
                return True
            else:
                return False
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Div(,Hello page!)", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        res = self.call("NewPage", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        asserts = ["hash"]
        auth_res = self.check_post_api("/content/hash/" + name, "", asserts)
        not_auth_res = requests.post(self.url + "/content/hash/" + name)
        not_auth_res = not_auth_res.json()
        page = "not_exist_page_xxxxxxxxx"
        not_auth_res_not_exist = requests.post(self.url + "/content/hash/" + page)
        not_auth_res_not_exist = not_auth_res_not_exist.json()
        must_be = dict(authRes=True,
                      notAuthRes=True,
                      msg="Page not found")
        actual = dict(authRes=is_hash_not_empty(auth_res),
                      notAuthRes=is_hash_not_empty(not_auth_res),
                      msg=not_auth_res_not_exist["msg"])
        self.unit.assertDictEqual(must_be, actual, "Not all assertions passed in test_content_hash")

    def test_get_ecosystem_name(self):
        id = 1
        asserts = ["ecosystem_name"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts)

    def test_get_ecosystem_name_new(self):
        data = {"Name": "ecos_" + tools.generate_random_name()}
        res = self.call("NewEcosystem", data)
        id = self.check_get_api("/list/ecosystems", "", [])["count"]
        asserts = ["ecosystem_name"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts)

    def test_get_ecosystem_name_incorrect(self):
        id = 99999
        asserts = ["error"]
        self.check_get_api("/ecosystemname?id=" + str(id), "", asserts)

