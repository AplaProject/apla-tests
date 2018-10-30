import unittest
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


    def test_keyinfo_by_address(self):
        res = api.keyinfo(self.url, self.token, self.data['address'])
        for item in res:
            if len(item) > 2:
                asserts = {'ecosystem', 'name', 'roles'}
            else:
                asserts = {'ecosystem', 'name'}
            self.check_result(item, asserts)


    def test_keyinfo_by_keyid(self):
        res = api.keyinfo(self.url, self.token, self.data['key_id'])
        for item in res:
            if len(item) > 2:
                asserts = {'ecosystem', 'name', 'roles'}
            else:
                asserts = {'ecosystem', 'name'}
            self.check_result(item, asserts)


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
        asserts = ['error', 'msg']
        res = api.contract(self.url, self.token, contract)
        error = "E_CONTRACT"
        msg = "There is not " + contract + " contract"
        self.check_result(res, asserts, error, msg)


    def test_content_lang(self):
        name_lang = "Lang_" + tools.generate_random_name()
        trans = """
        {
            "en": "World_en",
            "ru": "Мир_ru",
            "fr-FR": "Monde_fr-FR",
            "de": "Welt_de"
        }
        """
        data = {
            "Name": name_lang,
            "Trans": trans,
        }
        res = self.call("NewLang", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        name_page = "Page_" + tools.generate_random_name()
        value_page = "Hello, LangRes({})".format(name_lang)
        data_page = {
            "ApplicationId": 1,
            "Name": name_page,
            "Value": value_page,
            "Conditions": "true",
            "Menu": "default_menu"
        }
        res = self.call("NewPage", data_page)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello, World_en'}]
        content_ru = [{'tag': 'text', 'text': 'Hello, Мир_ru'}]
        content_fr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR'}]
        content_de = [{'tag': 'text', 'text': 'Hello, Welt_de'}]
        dict_exp = {
            "default": content,
            "ru": content_ru,
            "fr": content_fr,
            "de": content_de,
            "pe": content
        }
        p_content = actions.get_content(self.url, "page", name_page, "en", 1, self.token)       # should be: en
        ru_p_content = actions.get_content(self.url, "page", name_page, "ru", 1, self.token)    # should be: ru
        fr_p_content = actions.get_content(self.url, "page", name_page, "fr-FR", 1, self.token) # should be: fr-FR
        de_p_content = actions.get_content(self.url, "page", name_page, "de-DE", 1, self.token) # should be: de
        pe_p_content = actions.get_content(self.url, "page", name_page, "pe", 1, self.token)    # should be: en
        dict_cur = {
            "default" : p_content['tree'],
            "ru": ru_p_content['tree'],
            "fr": fr_p_content['tree'],
            "de": de_p_content['tree'],
            "pe": pe_p_content['tree']
        }
        self.unit.assertDictEqual(dict_cur, dict_exp, "One of langRes is faild")


    def test_content_lang_after_edit(self):
        name_lang = "Lang_" + tools.generate_random_name()
        trans = """
        {
            "en": "World_en",
            "ru": "Мир_ru",
            "fr-FR": "Monde_fr-FR",
            "de": "Welt_de"
        }
        """
        data = {
            "Name": name_lang,
            "Trans": trans
        }
        res = self.call("NewLang", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        name_page = "Page_" + tools.generate_random_name()
        value_page = "Hello, LangRes({})".format(name_lang)
        data_page = {
            "Name": name_page,
            "Value": value_page,
            "Conditions": "true",
            "Menu": "default_menu",
            "ApplicationId": 1
        }
        res = self.call("NewPage", data_page)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        count = actions.get_count(self.url, 'languages', self.token)
        trans_edit = """
        {
            "en": "World_en_ed",
            "ru": "Мир_ru_ed",
            "fr-FR": "Monde_fr-FR_ed",
            "de": "Welt_de_ed"
        }
        """
        data_edit = {
            "Id": count,
            "Trans": trans_edit
        }
        res = self.call("EditLang", data_edit)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        content = [{'tag': 'text', 'text': 'Hello, World_en_ed'}]
        content_ru = [{'tag': 'text', 'text': 'Hello, Мир_ru_ed'}]
        content_fr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR_ed'}]
        content_de = [{'tag': 'text', 'text': 'Hello, Welt_de_ed'}]
        dict_exp = {
            "default": content,
            "ru": content_ru,
            "fr": content_fr,
            "de": content_de,
            "pe": content
        }
        p_content = actions.get_content(self.url, "page", name_page, "en", 1, self.token)       # should be: en
        ru_p_content = actions.get_content(self.url, "page", name_page, "ru", 1, self.token)    # should be: ru
        fr_p_content = actions.get_content(self.url, "page", name_page, "fr-FR", 1, self.token) # should be: fr-FR
        de_p_content = actions.get_content(self.url, "page", name_page, "de-DE", 1, self.token) # should be: de
        pe_p_content = actions.get_content(self.url, "page", name_page, "pe", 1, self.token)    # should be: en
        dict_cur = {
            "default": p_content['tree'],
            "ru": ru_p_content['tree'],
            "fr": fr_p_content['tree'],
            "de": de_p_content['tree'],
            "pe": pe_p_content['tree']
        }
        self.unit.assertDictEqual(dict_cur, dict_exp, "One of langRes is faild")


    def test_get_content_from_template(self):
        template = "SetVar(mytest, 100) Div(Body: #mytest#)"
        res = api.content_template(self.url, self.token, template)
        answer_tree = {'tree': [{'tag': 'div', 'children': [{'tag': 'text', 'text': '100'}]}]}
        self.unit.assertEqual(answer_tree, res)


    def test_get_content_from_template_source(self):
        template = "SetVar(mytest, 100) Div(Body: #mytest#)"
        res = api.content_template(self.url, self.token, template, source=1)
        answer_tree = {'tree': [{'tag': 'setvar', 'attr': {'name': 'mytest', 'value': '100'}},
                                {'tag': 'div', 'children': [{'tag': 'text', 'text': '#mytest#'}]}]}
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
        res = api.content_source(self.url, self.token, name)
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
        value = "hello123"
        page_params = {"test": value}
        res = api.content(self.url, self.token, "page", name, page_params=page_params)
        self.unit.assertEqual(value, res["tree"][0]["text"])


    def test_get_content_from_another_ecosystem(self):
        # create new ecosystem
        ecosys_name = "Ecosys_" + tools.generate_random_name()
        data = {"Name": ecosys_name}
        res = self.call("NewEcosystem", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        ecosys_num = api.ecosystems(self.url, self.token)["number"]
        # login founder in new ecosystem
        data2 = actions.login(self.url, self.pr_key, 0, ecosys_num)
        token2 = data2["jwtToken"]
        # create page in new ecosystem
        page_name = "Page_" + tools.generate_random_name()
        page_text = "Page in {} ecosystem".format(ecosys_num)
        page_value = "Span({})".format(page_text)
        data = {
            "Name": page_name,
            "Value": page_value,
            'ApplicationId': 1,
            "Conditions": "true",
            "Menu": "default_menu"
        }
        resp = actions.call_contract(self.url, self.pr_key, "@1NewPage",
                                     data, token2, ecosystem=ecosys_num)
        status = actions.tx_status(self.url, self.wait, resp, token2)
        self.unit.assertGreater(status["blockid"], 0,
                                "BlockId is not generated: " + str(status))
        # create menu in new ecosystem
        menu_name = "Menu_" + tools.generate_random_name()
        menu_title = "Test menu"
        value = 'MenuItem(Title:"{}")'.format(menu_title)
        data = {
            "Name": menu_name,
            "Value": value,
            "Conditions": "true"
        }
        resp = actions.call_contract(self.url, self.pr_key, "@1NewMenu",
                                   data, token2, ecosystem=ecosys_num)
        status = actions.tx_status(self.url, self.wait, resp, token2)
        self.unit.assertGreater(status["blockid"], 0,
                                "BlockId is not generated: " + str(status))
        # test
        p_name = '@{ecosys_num}{page_name}'.format(
            ecosys_num=ecosys_num,
            page_name=page_name
        )
        m_name = '@{ecosys_num}{menu_name}'.format(
            ecosys_num=ecosys_num,
            menu_name=menu_name
        )
        res_page = api.content(self.url, self.token, 'page', p_name)
        res_menu = api.content(self.url, self.token, 'menu', m_name)
        must_be = dict(page_text=page_text,
                       menu=menu_title)
        expected_value = dict(page_text=res_page["tree"][0]["children"][0]["text"],
                              menu=res_menu["tree"][0]["attr"]["title"])
        self.unit.assertEqual(must_be, expected_value, "Dictionaries are different!")


    def test_get_back_api_version(self):
        asserts = ["."]
        res = api.version(self.url, self.token)
        self.check_result(res, asserts)


    def test_get_systemparams_all_params(self):
        asserts = ["list"]
        res = api.systemparams(self.url, self.token)
        self.check_result(res, asserts)
        self.unit.assertGreater(len(res["list"]), 0,
                                "Count of systemparams not Greater 0: " + str(len(res["list"])))


    def test_get_systemparams_some_param(self):
        asserts = ["list"]
        param = "gap_between_blocks"
        res = api.systemparams(self.url, self.token, param)
        self.check_result(res, asserts)
        self.unit.assertEqual(1, len(res["list"]))
        self.unit.assertEqual(param, res["list"][0]["name"])


    def test_get_systemparams_incorrect_param(self):
        asserts = ['error', 'msg']
        param = "not_exist_parameter"
        res = api.systemparams(self.url, self.token, param)
        error = 'E_PARAMNOTFOUND'
        msg = 'Parameter {param} has not been found'.format(param=param)
        self.check_result(res, asserts, error, msg)


    def test_get_contracts(self):
        limit = 25 # Default value without parameters
        asserts = ["list"]
        res = api.contracts(self.url, self.token)
        self.check_result(res, asserts)
        self.unit.assertEqual(limit, len(res["list"]))


    def test_get_contracts_limit(self):
        limit = 3
        asserts = ["list"]
        res = api.contracts(self.url, self.token, limit=limit)
        self.check_result(res, asserts)
        self.unit.assertEqual(limit, len(res["list"]))


    def test_get_contracts_offset(self):
        res = api.contracts(self.url, self.token)
        offset = res["count"]
        asserts = ["list"]
        res = api.contracts(self.url, self.token, offset=offset)
        self.check_result(res, asserts)
        self.unit.assertEqual(None, res["list"])


    def test_get_contracts_empty(self):
        limit = 99999
        offset = 99999
        asserts = ["list"]
        res = api.contracts(self.url, self.token, limit=limit, offset=offset)
        self.check_result(res, asserts)
        self.unit.assertEqual(None, res["list"])


    def test_get_interface_page(self):
        asserts = ["id"]
        page = "default_page"
        res = api.interface(self.url, self.token, 'page', page)
        self.check_result(res, asserts)
        self.unit.assertEqual("default_page", res["name"])


    def test_get_interface_page_incorrect(self):
        asserts = ["error", "msg"]
        page = "not_exist_page_xxxxxxxxxxx"
        res = api.interface(self.url, self.token, 'page', page)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)


    def test_get_interface_menu(self):
        asserts = ["id"]
        menu = "default_menu"
        res = api.interface(self.url, self.token, 'menu', menu)
        self.check_result(res, asserts)
        self.unit.assertEqual("default_menu", res["name"])


    def test_get_interface_menu_incorrect(self):
        asserts = ["error", "msg"]
        menu = "not_exist_menu_xxxxxxxxxxx"
        res = api.interface(self.url, self.token, 'page', menu)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)


    def test_get_interface_block(self):
        # Add new block
        block = "Block_" + tools.generate_random_name()
        data = {
            "Name": block,
            "Value": "Hello page!",
            "ApplicationId": 1,
            "Conditions": "true"
        }
        res = self.call("NewBlock", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        # Test
        asserts = ["id"]
        res = api.interface(self.url, self.token, 'block', block)
        self.check_result(res, asserts)
        self.unit.assertEqual(block, res["name"])


    def test_get_interface_block_incorrect(self):
        asserts = ["error", "msg"]
        block = "not_exist_block_xxxxxxxxxxx"
        res = api.interface(self.url, self.token, 'block', block)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)


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
        res = actions.is_wallet_created(self.url, self.token, data1["key_id"])
        self.unit.assertTrue(res, "Wallet for new user didn't created")


    def test_login2(self):
        is_one = False
        keys = tools.read_fixtures("keys")
        data1 = actions.login(self.url, keys["key3"], 0)
        time.sleep(5)
        res = actions.is_wallet_created(self.url, self.token, data1["key_id"])
        if res == True:
            data2 = actions.login(self.url, keys["key1"], 0)
            time.sleep(5)
            is_one = actions.is_wallet_created(self.url, self.token, data2["key_id"])
            self.unit.assertTrue(is_one, "Wallet for new user didn't created")


    def test_get_avatar_without_login(self):
        # add file in binaries
        name = "file_" + tools.generate_random_name()
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {
            "Name": name,
            "ApplicationId": 1,
            "DataMimeType":"image/jpeg",
            'Data': file
        }
        res = self.call("UploadBinary", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        last_rec = actions.get_count(self.url, 'binaries', self.token)
        founder_id = actions.get_object_id(self.url, 'founder', 'members', self.token)
        # change column permissions
        data = {
            'member_name': 'founder',
            'image_id': last_rec
        }
        res = self.call("ProfileEdit", data)
        self.unit.assertGreater(res, 0, "BlockId is not generated: " + str(res))
        # test
        resp = api.avatar(self.url, token='', member=founder_id, ecosystem=1)
        msg = "Content-Length is different!"
        self.unit.assertIn("71926", str(resp.headers["Content-Length"]), msg)


    def test_get_centrifugo_address_without_login(self):
        asserts = ['ws://']
        res = api.config_centrifugo(self.url, token='')
        self.check_result(res, asserts)


    def test_content_hash(self):
        name = "Page_" + tools.generate_random_name()
        data = {
            "Name": name,
            "Value": "Div(,Hello page!)",
            "ApplicationId": 1,
            "Conditions": "true",
            "Menu": "default_menu"
        }
        res = self.call("NewPage", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        res = api.content_hash(self.url, self.token, name)
        asserts = ['hash']
        self.check_result(res, asserts)


    def test_content_hash_incorrect(self):
        name = "not_exist_page_xxxxxxxxx"
        res = api.content_hash(self.url, self.token, name)
        asserts = ['error', 'msg']
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)


    def test_get_ecosystem_name(self):
        asserts = ["ecosystem_name"]
        res = api.ecosystemname(self.url, self.token, id=1)
        self.check_result(res, asserts)


    def test_get_ecosystem_name_new(self):
        name = "ecos_" + tools.generate_random_name()
        data = {"Name": name}
        res = self.call("NewEcosystem", data)
        self.unit.assertGreater(int(res), 0, "BlockId is not generated: " + str(res))
        id = actions.get_count(self.url, 'ecosystems', self.token)
        asserts = ["ecosystem_name"]
        res = api.ecosystemname(self.url, self.token, id=id)
        self.check_result(res, asserts)
        self.unit.assertEqual(res["ecosystem_name"], name,
                              'Name of ecosystem is not equals!')


    def test_get_ecosystem_name_incorrect(self):
        id = 99999
        res = api.ecosystemname(self.url, self.token, id=id)
        asserts = ['error', 'msg']
        error = 'E_PARAMNOTFOUND'
        msg = 'Parameter name has not been found'
        self.check_result(res, asserts, error, msg)
