import unittest
import os
import hashlib
import requests

from libs import actions, tools, api, check, contract


class TestApi():
    config = tools.read_config('nodes')
    url = config[1]['url']
    wait = tools.read_config('test')['wait_tx_status']
    pr_key = config[0]['private_key']
    data = actions.login(url, pr_key, 0)
    token = data['jwtToken']

    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()

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
            self.unit.assertDictEqual(
                expected, actual, 'Incorrect error ' + str(result))
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
        asserts = {'ecosystem', 'name'}
        new_pr_key = tools.generate_pr_key()
        new_user_data = actions.login(self.url, new_pr_key)
        check.is_new_key_in_keys(self.url, self.token,
                                 new_user_data['key_id'], self.wait)
        tx = contract.new_ecosystem(self.url,
                                    new_pr_key,
                                    new_user_data['jwtToken'],
                                    tools.generate_random_name())
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # test
        res = api.keyinfo(self.url, token='', key_id=new_user_data['address'])
        for item in res:
            self.check_result(item, asserts)
        self.unit.assertEqual(len(res), 2, 'Length response is not equals')

    def test_keyinfo_by_keyid(self):
        asserts = {'ecosystem', 'name', 'roles'}
        new_pr_key = tools.generate_pr_key()
        new_user_data = actions.login(self.url, new_pr_key)
        check.is_new_key_in_keys(self.url, self.token,
                                 new_user_data['key_id'], self.wait)
        data = {'rid': 2,
                'member_id': new_user_data['key_id']}
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    'RolesAssign',
                                    data,
                                    self.token)
        status = {'hash': res}
        check.is_tx_in_block(self.url, self.wait, status, self.token)
        # test
        res = api.keyinfo(self.url, token='', key_id=new_user_data['key_id'])
        for item in res:
            self.check_result(item, asserts)
        self.unit.assertEqual(len(res), 1, 'Length response is not equals')

    def test_keyinfo_by_address_incorrect(self):
        asserts = ['error', 'msg']
        address = '0000-0990-3244-5453-2310'
        error = 'E_INVALIDWALLET'
        msg = 'Wallet {adr} is not valid'.format(adr=address)
        res = api.keyinfo(self.url, token='', key_id=address)
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
        self.unit.assertEqual(
            actual, must_be, 'test_get_params_ecosystem_with_names is failed!')

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
                    self.unit.fail('Answer from API /table/' +
                                   table + ' is: ' + str(table_info))
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
        contract = 'contract'
        asserts = ['error', 'msg']
        res = api.contract(self.url, self.token, contract)
        error = 'E_CONTRACT'
        msg = 'There is not ' + contract + ' contract'
        self.check_result(res, asserts, error, msg)

    def test_content_lang(self):
        name_lang = 'Lang_' + tools.generate_random_name()
        trans = '''
        {
            "en": "World_en",
            "ru": "Мир_ru",
            "fr-FR": "Monde_fr-FR",
            "de": "Welt_de"
        }
        '''
        res = contract.new_lang(self.url,
                                self.pr_key,
                                self.token,
                                name_lang,
                                trans)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        name_page = 'Page_' + tools.generate_random_name()
        value_page = 'Hello, LangRes({})'.format(name_lang)
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                name_page,
                                value_page)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # test
        content = [{'tag': 'text', 'text': 'Hello, World_en'}]
        content_ru = [{'tag': 'text', 'text': 'Hello, Мир_ru'}]
        content_fr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR'}]
        content_de = [{'tag': 'text', 'text': 'Hello, Welt_de'}]
        dict_exp = {
            'default': content,
            'ru': content_ru,
            'fr': content_fr,
            'de': content_de,
            'pe': content
        }
        p_content = actions.get_content(
            self.url, 'page', name_page, 'en', 1, self.token)       # should be: en
        ru_p_content = actions.get_content(
            self.url, 'page', name_page, 'ru', 1, self.token)    # should be: ru
        fr_p_content = actions.get_content(
            self.url, 'page', name_page, 'fr-FR', 1, self.token)  # should be: fr-FR
        de_p_content = actions.get_content(
            self.url, 'page', name_page, 'de-DE', 1, self.token)  # should be: de
        pe_p_content = actions.get_content(
            self.url, 'page', name_page, 'pe', 1, self.token)    # should be: en
        dict_cur = {
            'default': p_content['tree'],
            'ru': ru_p_content['tree'],
            'fr': fr_p_content['tree'],
            'de': de_p_content['tree'],
            'pe': pe_p_content['tree']
        }
        self.unit.assertDictEqual(
            dict_cur, dict_exp, 'One of langRes is faild')

    def test_content_lang_after_edit(self):
        name_lang = 'Lang_' + tools.generate_random_name()
        trans = '''
        {
            "en": "World_en",
            "ru": "Мир_ru",
            "fr-FR": "Monde_fr-FR",
            "de": "Welt_de"
        }
        '''
        res = contract.new_lang(self.url,
                                self.pr_key,
                                self.token,
                                name_lang,
                                trans)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        name_page = 'Page_' + tools.generate_random_name()
        value_page = 'Hello, LangRes({})'.format(name_lang)
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                name_page,
                                value_page)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        count = actions.get_count(self.url, 'languages', self.token)
        trans_edit = '''
        {
            "en": "World_en_ed",
            "ru": "Мир_ru_ed",
            "fr-FR": "Monde_fr-FR_ed",
            "de": "Welt_de_ed"
        }
        '''
        res = contract.edit_lang(self.url,
                                 self.pr_key,
                                 self.token,
                                 count,
                                 trans_edit)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # test
        content = [{'tag': 'text', 'text': 'Hello, World_en_ed'}]
        content_ru = [{'tag': 'text', 'text': 'Hello, Мир_ru_ed'}]
        content_fr = [{'tag': 'text', 'text': 'Hello, Monde_fr-FR_ed'}]
        content_de = [{'tag': 'text', 'text': 'Hello, Welt_de_ed'}]
        dict_exp = {
            'default': content,
            'ru': content_ru,
            'fr': content_fr,
            'de': content_de,
            'pe': content
        }
        p_content = actions.get_content(
            self.url, 'page', name_page, 'en', 1, self.token)       # should be: en
        ru_p_content = actions.get_content(
            self.url, 'page', name_page, 'ru', 1, self.token)    # should be: ru
        fr_p_content = actions.get_content(
            self.url, 'page', name_page, 'fr-FR', 1, self.token)  # should be: fr-FR
        de_p_content = actions.get_content(
            self.url, 'page', name_page, 'de-DE', 1, self.token)  # should be: de
        pe_p_content = actions.get_content(
            self.url, 'page', name_page, 'pe', 1, self.token)    # should be: en
        dict_cur = {
            'default': p_content['tree'],
            'ru': ru_p_content['tree'],
            'fr': fr_p_content['tree'],
            'de': de_p_content['tree'],
            'pe': pe_p_content['tree']
        }
        self.unit.assertDictEqual(
            dict_cur, dict_exp, 'One of langRes is faild')

    def test_get_content_from_template(self):
        template = 'SetVar(mytest, 100) Div(Body: #mytest#)'
        res = api.content_template(self.url, self.token, template)
        answer_tree = {
            'tree': [{'tag': 'div', 'children': [{'tag': 'text', 'text': '100'}]}]}
        self.unit.assertEqual(answer_tree, res)

    def test_get_content_from_template_source(self):
        template = 'SetVar(mytest, 100) Div(Body: #mytest#)'
        res = api.content_template(self.url, self.token, template, source=1)
        answer_tree = {'tree': [{'tag': 'setvar', 'attr': {'name': 'mytest', 'value': '100'}},
                                {'tag': 'div', 'children': [{'tag': 'text', 'text': '#mytest#'}]}]}
        self.unit.assertEqual(answer_tree, res)

    def test_get_content_source(self):
        # Create new page for test
        name = 'Page_' + tools.generate_random_name()
        value = 'SetVar(a,"Hello") \n Div(Body: #a#)'
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                name,
                                value)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # Test
        res = api.content_source(self.url, self.token, name)
        childrenText = res['tree'][1]['children'][0]['text']
        self.unit.assertEqual('#a#', childrenText)

    def test_get_content_with_param_from_address_string(self):
        # Create new page for test
        name = 'Page_' + tools.generate_random_name()
        value = '#test#'
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                name,
                                value)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # Test
        value = 'hello123'
        page_params = {'test': value}
        res = api.content(self.url, self.token, 'page',
                          name, page_params=page_params)
        self.unit.assertEqual(value, res['tree'][0]['text'])

    def test_get_content_from_another_ecosystem(self):
        # create new ecosystem
        ecosys_name = 'Ecosys_' + tools.generate_random_name()
        res = contract.new_ecosystem(self.url,
                                     self.pr_key,
                                     self.token,
                                     ecosys_name)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        ecosys_num = api.ecosystems(self.url, self.token)['number']
        # login founder in new ecosystem
        data2 = actions.login(self.url, self.pr_key, 0, ecosys_num)
        token2 = data2['jwtToken']
        # create page in new ecosystem
        page_name = 'Page_' + tools.generate_random_name()
        page_text = 'Page in {} ecosystem'.format(ecosys_num)
        page_value = 'Span({})'.format(page_text)
        res = contract.new_page(self.url,
                                self.pr_key,
                                token2,
                                page_name,
                                page_value,
                                ecosystem=ecosys_num)
        check.is_tx_in_block(self.url, self.wait, res, token2)
        # create menu in new ecosystem
        menu_name = 'Menu_' + tools.generate_random_name()
        menu_title = 'Test menu'
        menu_value = 'MenuItem(Title:"{}")'.format(menu_title)
        res = contract.new_menu(self.url,
                                self.pr_key,
                                token2,
                                menu_name,
                                menu_value,
                                ecosystem=ecosys_num)
        check.is_tx_in_block(self.url, self.wait, res, token2)
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
        expected_value = dict(page_text=res_page['tree'][0]['children'][0]['text'],
                              menu=res_menu['tree'][0]['attr']['title'])
        self.unit.assertEqual(must_be, expected_value,
                              'Dictionaries are different!')

    def test_get_content_page_with_menu_from_different_ecosystems(self):
        page_name = 'Page_' + tools.generate_random_name()
        menu_name = 'Menu_' + tools.generate_random_name()
        ecosys_num = 1
        # create menu in first ecosystem
        menu_title1 = 'Test menu {}'.format(ecosys_num)
        menu_value = 'MenuItem(Title:"{}")'.format(menu_title1)
        res = contract.new_menu(self.url,
                                self.pr_key,
                                self.token,
                                menu_name,
                                menu_value,
                                ecosystem=ecosys_num)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # create page in first ecosystem
        page_text1 = 'Page in {} ecosystem'.format(ecosys_num)
        page_value = 'Span({})'.format(page_text1)
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                page_name,
                                page_value,
                                menu=menu_name,
                                ecosystem=ecosys_num)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        p_name1 = '@{ecosys_num}{page_name}'.format(
            ecosys_num=ecosys_num,
            page_name=page_name
        )
        # create new ecosystem
        ecosys_name = 'Ecosys_' + tools.generate_random_name()
        res = contract.new_ecosystem(self.url,
                                     self.pr_key,
                                     self.token,
                                     ecosys_name)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        ecosys_num = api.ecosystems(self.url, self.token)['number']
        # login founder in new ecosystem
        data2 = actions.login(self.url, self.pr_key, 0, ecosys_num)
        token2 = data2['jwtToken']
        # create menu in new ecosystem
        menu_title2 = 'Test menu {}'.format(ecosys_num)
        menu_value = 'MenuItem(Title:"{}")'.format(menu_title2)
        res = contract.new_menu(self.url,
                                self.pr_key,
                                token2,
                                menu_name,
                                menu_value,
                                ecosystem=ecosys_num)
        check.is_tx_in_block(self.url, self.wait, res, token2)
        # create page in new ecosystem
        page_text2 = 'Page in {} ecosystem'.format(ecosys_num)
        page_value = 'Span({})'.format(page_text2)
        res = contract.new_page(self.url,
                                self.pr_key,
                                token2,
                                page_name,
                                page_value,
                                menu=menu_name,
                                ecosystem=ecosys_num)
        check.is_tx_in_block(self.url, self.wait, res, token2)
        p_name2 = '@{ecosys_num}{page_name}'.format(
            ecosys_num=ecosys_num,
            page_name=page_name
        )
        # test
        res_page11 = api.content(self.url, self.token, 'page', p_name1)
        res_page12 = api.content(self.url, self.token, 'page', p_name2)
        res_page22 = api.content(self.url, token2, 'page', p_name2)
        res_page21 = api.content(self.url, token2, 'page', p_name1)
        expected = dict(
            page11=page_text1,
            page12=page_text2,
            menu11=menu_title1,
            menu12=menu_title1,
            page22=page_text2,
            page21=page_text1,
            menu22=menu_title2,
            menu21=menu_title2,
        )
        actual = dict(
            page11=res_page11['tree'][0]['children'][0]['text'],
            page12=res_page12['tree'][0]['children'][0]['text'],
            menu11=res_page11['menutree'][0]['attr']['title'],
            menu12=res_page12['menutree'][0]['attr']['title'],
            page22=res_page22['tree'][0]['children'][0]['text'],
            page21=res_page21['tree'][0]['children'][0]['text'],
            menu22=res_page22['menutree'][0]['attr']['title'],
            menu21=res_page21['menutree'][0]['attr']['title'],
        )
        self.unit.assertEqual(actual, expected,
                              'Dictionaries are different!')

    def test_get_back_api_version(self):
        asserts = ['.']
        res = api.version(self.url, self.token)
        self.check_result(res, asserts)

    def test_get_systemparams_all_params(self):
        asserts = ['list']
        res = api.systemparams(self.url, self.token)
        self.check_result(res, asserts)
        self.unit.assertGreater(len(res['list']), 0,
                                'Count of systemparams not Greater 0: ' + str(len(res['list'])))

    def test_get_systemparams_some_param(self):
        asserts = ['list']
        param = 'gap_between_blocks'
        res = api.systemparams(self.url, self.token, param)
        self.check_result(res, asserts)
        self.unit.assertEqual(1, len(res['list']))
        self.unit.assertEqual(param, res['list'][0]['name'])

    def test_get_systemparams_incorrect_param(self):
        asserts = ['error', 'msg']
        param = 'not_exist_parameter'
        res = api.systemparams(self.url, self.token, param)
        error = 'E_PARAMNOTFOUND'
        msg = 'Parameter {param} has not been found'.format(param=param)
        self.check_result(res, asserts, error, msg)

    def test_get_contracts(self):
        limit = 25  # Default value without parameters
        asserts = ['list']
        res = api.contracts(self.url, self.token)
        self.check_result(res, asserts)
        self.unit.assertEqual(limit, len(res['list']))

    def test_get_contracts_limit(self):
        limit = 3
        asserts = ['list']
        res = api.contracts(self.url, self.token, limit=limit)
        self.check_result(res, asserts)
        self.unit.assertEqual(limit, len(res['list']))

    def test_get_contracts_offset(self):
        res = api.contracts(self.url, self.token)
        offset = res['count']
        asserts = ['list']
        res = api.contracts(self.url, self.token, offset=offset)
        self.check_result(res, asserts)
        self.unit.assertEqual(None, res['list'])

    def test_get_contracts_empty(self):
        limit = 99999
        offset = 99999
        asserts = ['list']
        res = api.contracts(self.url, self.token, limit=limit, offset=offset)
        self.check_result(res, asserts)
        self.unit.assertEqual(None, res['list'])

    def test_get_interface_page(self):
        asserts = ['id']
        page = 'default_page'
        res = api.interface(self.url, self.token, 'page', page)
        self.check_result(res, asserts)
        self.unit.assertEqual('default_page', res['name'])

    def test_get_interface_page_incorrect(self):
        asserts = ['error', 'msg']
        page = 'not_exist_page_xxxxxxxxxxx'
        res = api.interface(self.url, self.token, 'page', page)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)

    def test_get_interface_menu(self):
        asserts = ['id']
        menu = 'default_menu'
        res = api.interface(self.url, self.token, 'menu', menu)
        self.check_result(res, asserts)
        self.unit.assertEqual('default_menu', res['name'])

    def test_get_interface_menu_incorrect(self):
        asserts = ['error', 'msg']
        menu = 'not_exist_menu_xxxxxxxxxxx'
        res = api.interface(self.url, self.token, 'page', menu)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)

    def test_get_interface_block(self):
        # Add new block
        block_name = 'Block_' + tools.generate_random_name()
        res = contract.new_block(self.url,
                                 self.pr_key,
                                 self.token,
                                 block_name)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # Test
        asserts = ['id']
        res = api.interface(self.url, self.token, 'block', block_name)
        self.check_result(res, asserts)
        self.unit.assertEqual(block_name, res['name'])

    def test_get_interface_block_incorrect(self):
        asserts = ['error', 'msg']
        block = 'not_exist_block_xxxxxxxxxxx'
        res = api.interface(self.url, self.token, 'block', block)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)

    def test_login(self):
        keys = tools.read_fixtures('keys')
        data1 = actions.login(self.url, keys['key5'], 0)
        check.is_new_key_in_keys(self.url, self.token,
                                 data1['key_id'], self.wait)
        res = actions.is_wallet_created(self.url, self.token, data1['key_id'])
        self.unit.assertTrue(res, 'Wallet for new user did not created')

    def test_login2(self):
        is_one = False
        keys = tools.read_fixtures('keys')
        data1 = actions.login(self.url, keys['key3'], 0)
        check.is_new_key_in_keys(self.url, self.token,
                                 data1['key_id'], self.wait)
        res = actions.is_wallet_created(self.url, self.token, data1['key_id'])
        if res:
            data2 = actions.login(self.url, keys['key1'], 0)
            check.is_new_key_in_keys(
                self.url, self.token, data2['key_id'], self.wait)
            is_one = actions.is_wallet_created(
                self.url, self.token, data2['key_id'])
            self.unit.assertTrue(is_one, 'Wallet for new user did not created')

    def test_get_avatar_without_login(self):
        # add file in binaries
        name = 'file_' + tools.generate_random_name()
        path = os.path.join(os.getcwd(), 'fixtures', 'image2.jpg')
        res = contract.upload_binary(self.url,
                                     self.pr_key,
                                     self.token,
                                     path,
                                     name)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        last_rec = actions.get_count(self.url, 'binaries', self.token)
        founder_id = actions.get_object_id(
            self.url, 'founder', 'members', self.token)
        # change avatar in profile
        data = {
            'member_name': 'founder',
            'image_id': last_rec
        }
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    'ProfileEdit',
                                    data,
                                    self.token)
        status = {'hash': res}
        check.is_tx_in_block(self.url, self.wait, status, self.token)
        # test
        resp = api.avatar(self.url, token='', member=founder_id, ecosystem=1)
        msg = 'Content-Length is different!'
        self.unit.assertIn('71926', str(resp.headers['Content-Length']), msg)

    def test_get_centrifugo_address_without_login(self):
        asserts = ['ws://']
        res = api.config_centrifugo(self.url, token='')
        self.check_result(res, asserts)

    def test_content_hash(self):
        name = 'Page_' + tools.generate_random_name()
        value = 'Div(,Hello page!)'
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                name,
                                value)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        res = api.content_hash(self.url, self.token, name)
        asserts = ['hash']
        self.check_result(res, asserts)

    def test_content_hash_incorrect(self):
        name = 'not_exist_page_xxxxxxxxx'
        res = api.content_hash(self.url, self.token, name)
        asserts = ['error', 'msg']
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)

    def test_get_ecosystem_name(self):
        asserts = ['ecosystem_name']
        res = api.ecosystemname(self.url, self.token, id=1)
        self.check_result(res, asserts)

    def test_get_ecosystem_name_new(self):
        name = 'ecos_' + tools.generate_random_name()
        res = contract.new_ecosystem(self.url,
                                     self.pr_key,
                                     self.token,
                                     name)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        id = actions.get_count(self.url, 'ecosystems', self.token)
        asserts = ['ecosystem_name']
        res = api.ecosystemname(self.url, self.token, id=id)
        self.check_result(res, asserts)
        self.unit.assertEqual(res['ecosystem_name'], name,
                              'Name of ecosystem is not equals!')

    def test_get_ecosystem_name_incorrect(self):
        id = 99999
        res = api.ecosystemname(self.url, self.token, id=id)
        asserts = ['error', 'msg']
        error = 'E_PARAMNOTFOUND'
        msg = 'Parameter name has not been found'
        self.check_result(res, asserts, error, msg)

    def test_compare_hashes(self):
        # Create new page for test
        name = 'Page_' + tools.generate_random_name()
        val = '''
            Div(Body: "New value of parameter - #test#)
            DBFind("contracts", src)
            Div(Body: "New value of parameter - #test#)
            DBFind("pages", src1)
            Div(Body: "New value of parameter - #test#)
            DBFind("blocks", src1)
            Div(,If(#role_id# == 0){Span(true)}.Else{Span(false)})
            Div(,If(#test# == 0){Span(#test#)}.Else{Span(false)})
            Div(,If(#test# == 1){Span(#test#)}.Else{Span(false)})
            Div(,If(#test# == 2){Span(#test#)}.Else{Span(false)})
            Div(,If(#test# == 3){Span(#test#)}.Else{Span(false)})
            Div(,If(#test# == 4){Span(#test#)}.Else{Span(false)})
            DBFind("contracts", src)
            Div(,If(#test# != 0){Span(true0)}.Else{Div(#test#)})
            Div(,If(#test# != 1){Span(true1)}.Else{Div(#test#)})
            Div(,If(#test# != 2){Span(true2)}.Else{Div(#test#)})
            Div(,If(#test# != 3){Span(true3)}.Else{Div(#test#)})
            Div(,If(#test# != 4){Span(true4)}.Else{Div(#test#)})
            Div(, Calculate(10000-(34+5)*#test#))
        '''
        res = contract.new_page(self.url, self.pr_key, self.token, name=name, value=val)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # Function, which get hashes
        def get_hashes(test):
            # Get content from page for getting hash
            founderID = actions.get_parameter_value(self.url, 'founder_account', self.token)
            my_login = actions.login(self.url, self.pr_key, role=0, ecosystem=1)
            token1 = my_login['jwtToken']
            data_content = {
                'test': test,
                'lang': 'en',
                'ecosystem': 1,
                'keyID': founderID,
                'roleID': 0,
            }
            full_url = self.url + '/content/page/' + name
            res = requests.post(full_url, params=data_content, headers={'Authorization': token1})
            m = hashlib.sha256()
            m.update(res.content)
            sha = m.hexdigest()
            # Get hash from page
            full_url = self.url + '/content/hash/' + name
            hash = requests.post(full_url, params=data_content)
            hash = hash.json()
            return sha, hash['hash']

        sha_list = {}
        hash_list = {}
        i = 0
        while i < 100:
            sha_from_content, hash = get_hashes(str(i))
            sha_list[i] = sha_from_content
            hash_list[i] = hash
            i += 1
        self.unit.assertDictEqual(sha_list, hash_list, 'Hashes is not equals')

    def test_appcontent_in_first_ecosystem(self):
        app_id = 1
        expected = {
            'blocks': len(actions.get_list(self.url, 'blocks', self.token, app_id)['list']),
            'pages': len(actions.get_list(self.url, 'pages', self.token, app_id)['list']),
            'contracts': len(actions.get_list(self.url, 'contracts', self.token, app_id)['list'])
        }
        asserts = ['blocks', 'pages', 'contracts']
        res = api.appcontent(self.url, self.token, appid=app_id, ecosystem=1)
        actual = {
            'blocks': len(res['blocks']),
            'pages': len(res['pages']),
            'contracts': len(res['contracts'])
        }
        self.check_result(res, asserts)
        self.unit.assertEqual(expected, actual, 'Dict is nor equals')

    def test_appcontent_in_new_ecosystem(self):
        # create new ecosystem
        res = contract.new_ecosystem(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        ecos_id = actions.get_count(self.url, 'ecosystems', self.token)
        new_data = actions.login(self.url, self.pr_key, ecosystem=ecos_id)
        new_token = new_data['jwtToken']
        app_id = actions.get_list(self.url, 'applications', new_token)['list'][0]['id']
        # test
        expected = {
            'blocks': int(actions.get_count(self.url, 'blocks', new_token)),
            'pages': int(actions.get_count(self.url, 'pages', new_token)),
            'contracts': int(actions.get_count(self.url, 'contracts', new_token))
        }
        asserts = ['blocks', 'pages', 'contracts']
        res = api.appcontent(self.url, self.token, appid=app_id, ecosystem=ecos_id)
        actual = {
            'blocks': len(res['blocks']),
            'pages': len(res['pages']),
            'contracts': len(res['contracts'])
        }
        self.check_result(res, asserts)
        self.unit.assertEqual(expected, actual, 'Dict is nor equals')

    def test_appcontent_in_new_app(self):
        # create new app
        res = contract.new_application(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        app_id = int(actions.get_object_id(self.url, res['name'], 'applications', self.token))
        res = contract.new_contract(self.url, self.pr_key, self.token, app=app_id)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        res = contract.new_block(self.url, self.pr_key, self.token, app_id=app_id)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        res = contract.new_page(self.url, self.pr_key, self.token, app_id=app_id)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # test
        expected = {
            'blocks': len(actions.get_list(self.url, 'blocks', self.token, app_id)['list']),
            'pages': len(actions.get_list(self.url, 'pages', self.token, app_id)['list']),
            'contracts': len(actions.get_list(self.url, 'contracts', self.token, app_id)['list'])
        }
        asserts = ['blocks', 'pages', 'contracts']
        res = api.appcontent(self.url, self.token, app_id, ecosystem=1)
        actual = {
            'blocks': len(res['blocks']),
            'pages': len(res['pages']),
            'contracts': len(res['contracts'])
        }
        self.check_result(res, asserts)
        self.unit.assertEqual(expected, actual, 'Dict is nor equals')

    def test_appcontent_incorrect_ecosystem(self):
        asserts = ['error', 'msg']
        ecos_id = 9999
        res = api.appcontent(self.url, self.token, appid=1, ecosystem=ecos_id)
        error = 'E_ECOSYSTEM'
        msg = "Ecosystem {} doesn't exist".format(ecos_id)
        self.check_result(res, asserts, error, msg)

    def test_block(self):
        asserts = ['hash',
                   'ecosystem_id',
                   'key_id',
                   'time',
                   'tx_count',
                   'rollbacks_hash',
                   'node_position']
        id = 1
        res = api.block(self.url, self.token, id)
        self.check_result(res, asserts)

    def test_block_incorrect(self):
        asserts = ['error', 'msg']
        id = 9999
        res = api.block(self.url, self.token, id)
        error = 'E_NOTFOUND'
        msg = 'Page not found'
        self.check_result(res, asserts, error, msg)

    def test_get_sections(self):
        asserts = ['count', 'list']
        res = api.sections(self.url, self.token)
        sec_count = actions.get_count(self.url, 'sections', self.token)
        self.check_result(res, asserts)
        self.unit.assertEqual(int(sec_count), int(res['count']), 'Dict is nor equals')

    def test_get_section_lang(self):
        # add new langres
        lang_name = tools.generate_random_name()
        en_title = 'NewSection'
        ru_title = 'НоваяСекция'
        trans = '{"en": "' + en_title + '", "ru" : "' + ru_title + '"}'
        res = contract.new_lang(self.url, self.pr_key, self.token,
                                name=lang_name, trans=trans)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # add new section
        res = contract.new_section(self.url, self.pr_key, self.token,
                                   title='$' + lang_name + '$')
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # test
        count = int(actions.get_count(self.url, 'sections', self.token))
        en_res = api.sections(self.url, self.token,
                           limit=1, offset=count-1, lang='en')
        ru_res = api.sections(self.url, self.token,
                           limit=1, offset=count-1, lang='ru')
        expected = {
            'en': en_title,
            'ru': ru_title
        }
        actual = {
            'en': en_res['list'][0]['title'],
            'ru': ru_res['list'][0]['title']
        }
        self.unit.assertEqual(expected, actual, 'Dict is not equals')
    # off
    def get_section_avalible_users(self):
        # change langres name on static name from section
        sections = actions.get_list(self.url, 'sections', self.token)
        sec_list = sections['list']
        for el in sec_list:
            if '$' in el['title']:
                res = contract.edit_section(self.url, self.pr_key, self.token,
                                            id=int(el['id']),
                                            title=tools.generate_random_name())
                check.is_tx_in_block(self.url, self.wait, res, self.token)
        # add new section
        admin_role = '1'
        res = contract.new_section(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # add role for section
        count = int(actions.get_count(self.url, 'sections', self.token))
        res = contract.section_roles(self.url, self.pr_key, self.token,
                                     id=int(count),
                                     rid=admin_role,
                                     operation='add')
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # test
        # added elements in expected dicts
        sections = actions.get_list(self.url, 'sections', self.token)
        count = int(sections['count'])
        sec_list = sections['list']
        expected_admin = {}
        expected_user = {}
        for el in sec_list:
            if el['roles_access'] == '[]':
                expected_user[el['id']] = el['title']
                expected_admin[el['id']] = el['title']
            if admin_role in el['roles_access']:
                expected_admin[el['id']] = el['title']
        # added elements in actual_admin dict
        actual_admin = {}
        token_admin = actions.login(self.url, self.pr_key,
                                    role=admin_role)['jwtToken']
        res_admin = api.sections(self.url, token_admin,
                                 limit=count)
        res_admin_list = res_admin['list']
        for el in res_admin_list:
            actual_admin[el['id']] = el['title']
        # added elements in actual_user dict
        actual_user = {}
        token_user = actions.login(self.url,
                               tools.generate_pr_key())['jwtToken']
        res_user = api.sections(self.url, token_user,
                                 limit=count)
        res_user_list = res_user['list']
        for el in res_user_list:
            actual_user[el['id']] = el['title']
        self.unit.assertEqual(expected_admin, actual_admin, 'Dict admin is not equals')
        self.unit.assertEqual(expected_user, actual_user, 'Dict user is not equals')
