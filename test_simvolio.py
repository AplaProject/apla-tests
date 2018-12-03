import hashlib
import unittest

from libs import actions, db, tools, contract as contracts, check


class TestSimvolio():
    contracts = tools.read_fixtures_yaml('simvolio')
    wait = tools.read_config('test')['wait_tx_status']
    config = tools.read_config('nodes')
    unit = unittest.TestCase()

    def setup(self):
        print('setup class')
        self.url = self.config[1]['url']
        self.pr_key = self.config[0]['private_key']
        self.db1 = self.config[0]['db']
        data = actions.login(self.url, self.pr_key, 0)
        self.token = data['jwtToken']

    def check_contract(self, sourse, check_point, data={}):
        tx = contracts.new_contract(
            self.url, self.pr_key, self.token, source=sourse)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        res = actions.call_contract(
            self.url, self.pr_key, tx['name'], data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertIn(check_point, result['result'], 'ERROR: ' +
                           str(result))

    def test_contract_dbFind(self):
        contract = self.contracts['dbFind']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_toUpper(self):
        contract = self.contracts['toUpper']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_elseif(self):
        contract = self.contracts['elseif']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_blockTime(self):
        contract = self.contracts['blockTime']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_ecosysParam(self):
        contract = self.contracts['ecosysParam']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_ifMap(self):
        contract = self.contracts['ifMap']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_dbRow(self):
        contract = self.contracts['dbRow']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_evalCondition(self):
        contract = self.contracts['evalCondition']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_validateCondition(self):
        contract = self.contracts['validateCondition']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_addressToId(self):
        contract = self.contracts['addressToId']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_idToAddress(self):
        contract = self.contracts['idToAddress']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_one(self):
        contract = self.contracts['one']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_row(self):
        contract = self.contracts['row']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_contains(self):
        contract = self.contracts['contains']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_float(self):
        contract = self.contracts['float']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_hasPrefix(self):
        contract = self.contracts['hasPrefix']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_hexToBytes(self):
        contract = self.contracts['hexToBytes']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_int(self):
        contract = self.contracts['int']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_join(self):
        contract = self.contracts['join']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_split(self):
        contract = self.contracts['split']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_len(self):
        contract = self.contracts['len']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_pubToID(self):
        contract = self.contracts['pubToID']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_replace(self):
        contract = self.contracts['replace']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_size(self):
        contract = self.contracts['size']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_sha256(self):
        contract = self.contracts['sha256']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_sprintf(self):
        contract = self.contracts['sprintf']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_str(self):
        contract = self.contracts['str']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_substr(self):
        contract = self.contracts['substr']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_sysParamString(self):
        contract = self.contracts['sysParamString']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_sysParamInt(self):
        contract = self.contracts['sysParamInt']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_getContractByName(self):
        contract = self.contracts['getContractByName']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_random(self):
        contract = self.contracts['random']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_getBlock(self):
        contract = self.contracts['getBlock']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_bool(self):
        contract = self.contracts['type_bool']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_bytes(self):
        contract = self.contracts['type_bytes']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_int(self):
        contract = self.contracts['type_int']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_address(self):
        contract = self.contracts['type_address']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_array(self):
        contract = self.contracts['type_array']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_map(self):
        contract = self.contracts['type_map']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_money(self):
        contract = self.contracts['type_money']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_float(self):
        contract = self.contracts['type_float']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_type_string(self):
        contract = self.contracts['type_string']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_getColumnType(self):
        contract = self.contracts['getColumnType']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_decodeBase64(self):
        contract = self.contracts['decodeBase64']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_encodeBase64(self):
        contract = self.contracts['encodeBase64']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_jsonEncode(self):
        contract = self.contracts['jsonEncode']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_jsonDecode(self):
        contract = self.contracts['jsonDecode']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_bytesToString(self):
        contract = self.contracts['bytesToString']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_stringToBytes(self):
        contract = self.contracts['stringToBytes']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_append(self):
        contract = self.contracts['append']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_getMapKeys(self):
        contract = self.contracts['getMapKeys']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_sortedKeys(self):
        contract = self.contracts['sortedKeys']
        self.check_contract(contract['code'], contract['asert'])
        
    def test_del_table_not_empty(self):
        contractName = 'SimvolioDelTab'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_table']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tab = 'contracts'
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {"table": tab}, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertEqual(result['error'], 'Table 1_' + tab + ' is not empty',
                              'Erorr in deleting tables by DelTab funtion')
        
    def test_del_table_not_present(self):
        contractName = 'SimvolioDelTab'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_table']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tab = 'kjkb'
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {"table": tab}, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertEqual(result['error'], 'Table 1_' + tab + ' has not been found',
                              'Erorr in deleting tables by DelTab funtion' + result['error'])
        
    def test_del_table_empty(self):
        contractName = 'SimvolioDelTab'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_table']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx_tab = contracts.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_tab, self.token)
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {"table": tx_tab['name']}, self.token)
        check.is_tx_in_block(self.url, self.wait, {'hash': res}, self.token)
        
    def test_del_column_not_empty(self):
        contractName = 'SimvolioDelColumn'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_column']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tab = 'contracts'
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {'table': tab, 'col': 'name'}, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertEqual(result['error'], 'Table 1_' + tab + ' is not empty',
                              'Erorr in deleting tables by DelTab funtion' + result['error'])
        
    def test_del_column_not_present_table(self):
        contractName = 'SimvolioDelColumn'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_column']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tab = 'notpresent'
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {'table': tab, 'col': 'name'}, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertEqual(result['error'], 'Table 1_' + tab + ' has not been found',
                              'Erorr in deleting tables by DelTab funtion' + result['error'])
        
    def test_del_column_not_present_column(self):
        contractName = 'SimvolioDelColumn'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_column']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx_tab = contracts.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_tab, self.token)
        col = "notpresent"
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {'table': tx_tab['name'], 'col': col}, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        self.unit.assertEqual(result['error'], 'column ' + col + " doesn't exist",
                              'Erorr in deleting tables by DelTab funtion' + result['error'])
        
    def test_del_column_not_empty(self):
        contractName = 'SimvolioDelColumn'
        if not actions.is_contract_present(self.url, self.token, contractName):
            contract = self.contracts['del_column']
            tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                        source=contract['code'], name = contractName)
            check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx_tab = contracts.new_table(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_tab, self.token)
        tx2 = contracts.new_column(self.url, self.pr_key, self.token, tx_tab['name'])
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        res = actions.call_contract(self.url, self.pr_key, contractName,
                                    {'table': tx_tab['name'], 'col': tx2['name']}, self.token)
        check.is_tx_in_block(self.url, self.wait, {'hash': res}, self.token)


    def test_contract_langRes(self):
        name = 'lang_' + tools.generate_random_name()
        trans = '{"en": "test_en", "de": "test_de"}'
        tx = contracts.new_lang(self.url, self.pr_key, self.token,
                                name=name, trans=trans)
        check.is_tx_in_block(self.url, self.wait, tx, self.token,)
        contract = self.contracts['langRes']
        data = {'Name': name}
        self.check_contract(contract['code'], contract['asert'], data)

    def test_contract_dbInsert(self):
        columns = '''[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]'''
        tx = contracts.new_table(self.url, self.pr_key, self.token, columns=columns,
                                 name='test')
        actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        contract = self.contracts['dbInsert']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_dbUpdate(self):
        columns = '''[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]'''
        tx = contracts.new_table(self.url, self.pr_key, self.token, columns=columns,
                                 name='test')
        actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        contract = self.contracts['dbInsert']
        self.check_contract(contract['code'], contract['asert'])
        contract = self.contracts['dbUpdate']
        self.check_contract(contract['code'], contract['asert'])
        list = actions.get_list(self.url, 'test', self.token)['list']
        for el in range(len(list)):
            if int(list[el]['id']) == 1:
                self.unit.assertEqual(
                    'updated', list[el]['test'], 'Failed. dbUpdate Error!')
                break

    def test_contracts_dbUpdateExt(self):
        columns = '''[{"name":"name","type":"varchar",
        "index": "1",  "conditions":"true"},
        {"name":"test","type":"varchar",
        "index": "0",  "conditions":"true"}]'''
        tx = contracts.new_table(self.url, self.pr_key, self.token, columns=columns,
                                 name='test')
        actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        contract = self.contracts['dbInsert']
        self.check_contract(contract['code'], contract['asert'])
        contract = self.contracts['dbUpdateExt']
        self.check_contract(contract['code'], contract['asert'])

    def test_contract_callContract(self):
        contract = self.contracts['myContract']
        inner_contract_name = tools.generate_random_name()
        tx = contracts.new_contract(self.url, self.pr_key, self.token,
                                    source=contract['code'],
                                    name=inner_contract_name)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        contract = self.contracts['callContract']
        data = {'Name': inner_contract_name}
        self.check_contract(contract['code'], contract['asert'], data)

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
            code = ' { data{ } conditions{ } action{ ' + \
                var_list[i] + ' = 5 } }'
            tx = contracts.new_contract(
                self.url, self.pr_key, self.token, source=code)
            st = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
            exp_result = 'system variable ' + \
                var_list[i] + ' cannot be changed'
            expexted_dict[i] = exp_result
            actual_dict[i] = st['error']
            self.unit.assertDictEqual(
                expexted_dict, actual_dict, 'Dictionaries is different')

    def get_metrics(self, ecosystem_num, metric_name):
        # get metrics count
        res = actions.get_list(self.url, 'metrics', self.token)
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
                code = ' {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }'
                tx = contracts.new_contract(
                    self.url, self.pr_key, self.token, source=code)
                current_block_id = check.is_tx_in_block(
                    self.url, self.wait, tx, self.token)
                old_block_id = current_block_id
        # generate contract which return count blocks in blockchain
        code2 = ' {\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }'
        tx2 = contracts.new_contract(
            self.url, self.pr_key, self.token, source=code2)
        current_block_id = check.is_tx_in_block(
            self.url, self.wait, tx2, self.token)
        # wait until generated 100 blocks
        if current_block_id < 100:
            wait_block_id(current_block_id, 100)
        # wait until generated multiples of 100 blocks
        if (current_block_id % 100 >= 90):
            count = current_block_id + (100 - (current_block_id % 100))
            wait_block_id(current_block_id, count)
        # test
        ecosystem_tx = self.get_metrics(1, 'ecosystem_tx')
        contract = self.contracts['dbSelectMetricsMin']
        self.check_contract(contract['code'], str(ecosystem_tx))

    def test_z2_db_select_metrics_max(self):
        # Run test after test_z1_db_select_metrics_min
        ecosystem_members = self.get_metrics(1, 'ecosystem_members')
        contract = self.contracts['dbSelectMetricsMax']
        self.check_contract(contract['code'], str(ecosystem_members))

    def test_z3_db_select_metrics_max(self):
        # Run test after test_z1_db_select_metrics_min
        ecosystem_pages = self.get_metrics(1, 'ecosystem_pages')
        contract = self.contracts['dbSelectMetricsAvg']
        self.check_contract(contract['code'], str(ecosystem_pages))

    def test_get_history_contract(self):
        # create contract
        replaced_string = 'old_var'
        code = '''
        {
            data{}
            conditions{}
            action{ var %s int }
        }
        ''' % replaced_string
        tx = contracts.new_contract(
            self.url, self.pr_key, self.token, source=code)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # change contract
        id = actions.get_object_id(
            self.url, tx['name'], 'contracts', self.token)
        new_code = code.replace(replaced_string, 'new_var')
        tx = contracts.edit_contract(self.url, self.pr_key, self.token, id,
                                     new_source=new_code)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # test
        data = {'Table': 'contracts', 'ID': id}
        contract = self.contracts['getHistory']
        self.check_contract(contract['code'], replaced_string, data)

    def test_get_history_page(self):
        # create page
        page = 'Div(Body: Hello)'
        tx_page = contracts.new_page(
            self.url, self.pr_key, self.token, value=page)
        check.is_tx_in_block(self.url, self.wait, tx_page, self.token)
        # change page
        id = actions.get_object_id(
            self.url, tx_page['name'], 'pages', self.token)
        new_value_page = page.replace('Hello', 'new_var')
        tx = contracts.edit_page(
            self.url, self.pr_key, self.token, id, value=new_value_page)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # test
        data = {'Table': 'pages', 'ID': id}
        contract = self.contracts['getHistory']
        self.check_contract(contract['code'], page, data)

    def test_sys_var_stack(self):
        # This test has not a fixture
        inner_name = tools.generate_random_name()
        innerBody = '''
                {
                data{}
                conditions{}
                action {
                    $result = $stack
                    }
                }
                '''
        inner_res = contracts.new_contract(self.url, self.pr_key, self.token,
                                           source=innerBody, name=inner_name)
        check.is_tx_in_block(self.url, self.wait, inner_res, self.token)
        outer_name = tools.generate_random_name()
        outer_body = '''
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
                ''' % inner_name
        outer_res = contracts.new_contract(self.url, self.pr_key, self.token,
                                           source=outer_body, name=outer_name)
        check.is_tx_in_block(self.url, self.wait, outer_res, self.token)
        result = actions.call_contract(
            self.url, self.pr_key, outer_name, {}, self.token)
        res = actions.tx_status(self.url, self.wait, result, self.token)
        must_be = '[@1' + outer_res['name'] + ' @1' + inner_res['name'] + ']'
        self.unit.assertEqual(
            must_be, res['result'], 'test_sys_var_stack is failed!')

    def test_get_history_row_menu(self):
        # create menu
        rollc_before = db.get_max_id_from_table(self.db1, 'rollback_tx')
        value = 'This is new menu'
        menu = contracts.new_menu(
            self.url, self.pr_key, self.token, value=value)
        check.is_tx_in_block(self.url, self.wait, menu, self.token)
        rollc_after = db.get_max_id_from_table(self.db1, 'rollback_tx')
        # change menu
        id = actions.get_object_id(self.url, menu['name'], 'menu', self.token)
        new_value_menu = value.replace('new menu', 'new_var')
        menu_e = contracts.edit_menu(self.url, self.pr_key, self.token,
                                     id, value=new_value_menu)
        check.is_tx_in_block(self.url, self.wait, menu_e, self.token)
        # test
        query = '''SELECT id FROM "rollback_tx" WHERE table_name = '1_menu' AND data='' AND id >= %s AND id <= %s''' % (
            rollc_before, rollc_after)
        rollback_id = db.submit_query(query, self.db1)[0][0]
        data = {'Table': 'menu', 'ID': id, 'rID': rollback_id}
        contract = self.contracts['getHistoryRow']
        self.check_contract(contract['code'], value, data)

    def test_get_history_row_block(self):
        # create block
        rollc_before = db.get_max_id_from_table(self.db1, 'rollback_tx')
        value = 'Div(Body: Hello)'
        block = contracts.new_block(
            self.url, self.pr_key, self.token, value=value)
        check.is_tx_in_block(self.url, self.wait, block, self.token)
        rollc_after = db.get_max_id_from_table(self.db1, 'rollback_tx')
        # change block
        id = actions.get_object_id(
            self.url, block['name'], 'blocks', self.token)
        new_value_block = value.replace('Hello', 'new_var')
        block_e = contracts.edit_block(self.url, self.pr_key, self.token, id,
                                       value=new_value_block)
        check.is_tx_in_block(self.url, self.wait, block_e, self.token)
        # test
        query = '''SELECT id FROM "rollback_tx" WHERE table_name = '1_blocks' AND data='' AND id >= %s AND id <= %s''' % (
            rollc_before, rollc_after)
        rollback_id = db.submit_query(query, self.db1)[0][0]
        print(rollback_id)
        data = {'Table': 'blocks', 'ID': id, 'rID': rollback_id}
        contract = self.contracts['getHistoryRow']
        self.check_contract(contract['code'], value, data)

    def test_contract_hash(self):
        my_string = 'Text message'
        cont_value = '''
        {
            action {
                $result = Hash("%s")
            }
        }
        ''' % my_string
        res = contracts.new_contract(self.url,
                                     self.pr_key,
                                     self.token,
                                     source=cont_value)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    res['name'],
                                    {},
                                    self.token)
        res = actions.tx_status(self.url, self.wait, res, self.token)
        m = hashlib.sha256()
        m.update(bytes(my_string, 'utf-8'))
        sha = m.hexdigest()
        self.unit.assertEqual(res['result'], sha, 'Hashes is not equals.')

    def test_types_of_data(self):
        data = {"B": "true",
                "B2": "true",
                "B3": "true"}
        contract = self.contracts['types_of_data']
        self.check_contract(contract['code'], contract['asert'], data)

    def test_types_of_data_incorrect(self):
        contract = self.contracts['types_of_data_incorrect']
        tx = contracts.new_contract(
            self.url, self.pr_key, self.token, source=contract['code'])
        result = actions.tx_status(self.url, self.wait, tx['hash'], self.token)
        self.unit.assertEqual(result['error'], contract['asert'], 'Error messages is different')