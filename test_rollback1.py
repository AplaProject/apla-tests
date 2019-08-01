import unittest
import json
import os

from libs import (actions,
                  tools,
                  db,
                  loger,
                  contract,
                  check)


class TestRollback1():
    conf = tools.read_config('main')
    url = conf['url']
    pr_key = conf['private_key']
    db_node = conf['db']
    l_data = actions.login(url, pr_key, 0)
    token = l_data['jwtToken']
    wait = tools.read_config('test')['wait_tx_status']
    log = loger.create_loger(__name__)

    def setup_class(self):
        self.unit = unittest.TestCase()

    def create_empty_contract(self):
        conditions = 'ContractConditions("MainCondition")'
        res = contract.new_contract(self.url,
                                    self.pr_key,
                                    self.token,
                                    condition=conditions)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return res['name'], res['code']

    def add_notification(self):
        # create contract, wich added record in notifications table
        body = '''
        {
        data {}
        conditions {}
        action {
            DBInsert("notifications", {"recipient->member_id": "-8399130570195839739",
                                        "notification->type": 1,
                                        "notification->header": "Message header",
                                        "notification->body": "Message body"})
            }
        }
        '''
        name = tools.generate_random_name()
        condition = 'ContractConditions("MainCondition")'
        res = contract.new_contract(self.url,
                                    self.pr_key,
                                    self.token,
                                    body,
                                    name,
                                    condition=condition)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # change permission for notifications table
        table_name = 'notifications'
        res = contract.edit_table(self.url,
                                  self.pr_key,
                                  self.token,
                                  name=table_name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # call contract, wich added record in notification table
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    name,
                                    {},
                                    self.token)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, {'hash': res}, self.token)
        # change permission for notifications table back
        insert = 'ContractAccess("Notifications_Single_Send_map","Notifications_Roles_Send_map")'
        update = 'ContractConditions("MainCondition")'
        read = 'ContractConditions("MainCondition")'
        column = 'ContractConditions("MainCondition")'
        res = contract.edit_table(self.url,
                                  self.pr_key,
                                  self.token,
                                  name=table_name,
                                  insert=insert,
                                  update=update,
                                  read=read,
                                  column=column)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def add_binary(self):
        name = 'image_' + tools.generate_random_name()
        path = os.path.join(os.getcwd(), 'fixtures', 'image2.jpg')
        res = contract.upload_binary(self.url,
                                     self.pr_key,
                                     self.token,
                                     path,
                                     name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def add_user_table(self):
        # add table
        columns = '''[{"name":"MyName","type":"varchar",
                    "index": "1", "conditions":"true"},
                    {"name":"ver_on_null","type":"varchar",
                    "index": "1", "conditions":"true"}]'''
        permission = '''{"read": "true",
                        "insert": "true",
                        "update": "true",
                        "new_column": "true"}'''
        table_name = 'rolltab_' + tools.generate_random_name()
        res = contract.new_table(self.url,
                                 self.pr_key,
                                 self.token,
                                 table_name,
                                 columns,
                                 permission)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return table_name

    def insert_to_user_table(self, table_name):
        # create contarct, wich added record in created table
        body = '''
        {
        data {}
        conditions {}
        action {
            DBInsert("%s", {MyName: "insert"})
            }
        }
        ''' % table_name
        name = tools.generate_random_name()
        res = contract.new_contract(self.url,
                                    self.pr_key,
                                    self.token,
                                    body,
                                    name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # call contarct, wich added record in created table
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    name,
                                    {},
                                    self.token)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, {'hash': res}, self.token)

    def update_user_table(self, table_name):
        # create contarct, wich updated record in created table
        body = '''
        {
        data {}
        conditions {}
        action {
            DBUpdate("%s", 1, {MyName: "update", ver_on_null: "update"})
            }
        }
        ''' % table_name
        name = tools.generate_random_name()
        res = contract.new_contract(self.url,
                                    self.pr_key,
                                    self.token,
                                    body,
                                    name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        # call contarct, wich added record in created table
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    name,
                                    {},
                                    self.token)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, {'hash': res}, self.token)

    def create_ecosystem(self):
        name = 'Ecosys' + tools.generate_random_name()
        res = contract.new_ecosystem(self.url,
                                     self.pr_key,
                                     self.token,
                                     name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def edit_contract(self, contract_name, code):
        id = actions.get_contract_id(self.url,
                                     contract_name,
                                     self.token)
        value = '{ data {} conditions {} action { var a map} }'
        res = contract.edit_contract(self.url,
                                     self.pr_key,
                                     self.token,
                                     id,
                                     value)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def bind_wallet(self, name):
        id = actions.get_contract_id(self.url, name, self.token)
        res = contract.bind_wallet(self.url,
                                   self.pr_key,
                                   self.token,
                                   id)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def unbind_wallet(self, name):
        id = actions.get_contract_id(self.url, name, self.token)
        res = contract.unbind_wallet(self.url,
                                     self.pr_key,
                                     self.token,
                                     id)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_parameter(self):
        name = 'Par_' + tools.generate_random_name()
        res = contract.new_parameter(self.url,
                                     self.pr_key,
                                     self.token,
                                     name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return name

    def edit_parameter(self, name):
        id = actions.get_parameter_id(self.url, name, self.token)
        value = 'test_edited'
        res = contract.edit_parameter(self.url,
                                      self.pr_key,
                                      self.token,
                                      id,
                                      value)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_menu(self):
        name = 'Menu_' + tools.generate_random_name()
        res = contract.new_menu(self.url,
                                self.pr_key,
                                self.token,
                                name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return name

    def edit_menu(self, name):
        id = actions.get_object_id(self.url, name, 'menu', self.token)
        print(id)
        value = 'ItemEdited'
        title = 'TitleEdited'
        res = contract.edit_menu(self.url,
                                 self.pr_key,
                                 self.token,
                                 id,
                                 value,
                                 title=title)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def append_memu(self, name):
        id = actions.get_object_id(self.url, name, 'menu', self.token)
        value = 'AppendedItem'
        res = contract.edit_menu(self.url,
                                 self.pr_key,
                                 self.token,
                                 id,
                                 value)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_page(self):
        name = 'Page_' + tools.generate_random_name()
        res = contract.new_page(self.url,
                                self.pr_key,
                                self.token,
                                name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return name

    def edit_page(self, name):
        id = actions.get_object_id(self.url, name, 'pages', self.token)
        value = 'Good by page!'
        res = contract.edit_page(self.url,
                                 self.pr_key,
                                 self.token,
                                 id,
                                 value=value)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def append_page(self, name):
        id = actions.get_object_id(self.url, name, 'pages', self.token)
        value = 'Good by!'
        res = contract.append_page(self.url,
                                   self.pr_key,
                                   self.token,
                                   id,
                                   value=value)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_block(self):
        name = 'Block_' + tools.generate_random_name()
        res = contract.new_block(self.url,
                                 self.pr_key,
                                 self.token,
                                 name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return name

    def edit_block(self, name):
        id = actions.get_object_id(self.url, name, 'blocks', self.token)
        value = 'Good by block!'
        res = contract.edit_block(self.url,
                                  self.pr_key,
                                  self.token,
                                  id,
                                  value)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_table(self):
        columns = '''[{"name":"MyName","type":"varchar",
                    "index": "1","conditions":"true"}]'''
        permission = '''{"read": "false",
                        "insert": "false",
                        "update" : "false",
                        "new_column": "false"}'''
        table_name = 'tab_' + tools.generate_random_name()
        res = contract.new_table(self.url,
                                 self.pr_key,
                                 self.token,
                                 table_name,
                                 columns,
                                 permission)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return table_name

    def edit_table(self, name):
        res = contract.edit_table(self.url,
                                  self.pr_key,
                                  self.token,
                                  name=name)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_column(self, table):
        col_name = 'Col_' + tools.generate_random_name()
        res = contract.new_column(self.url,
                                  self.pr_key,
                                  self.token,
                                  table=table,
                                  name=col_name,
                                  type='number')
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return col_name

    def edit_column(self, table, column):
        res = contract.edit_column(self.url,
                                   self.pr_key,
                                   self.token,
                                   table=table,
                                   column=column,
                                   update_perm='false',
                                   read_perm='false')
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def new_lang(self):
        name = 'Lang_' + tools.generate_random_name()
        res = contract.new_lang(self.url,
                                self.pr_key,
                                self.token)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)
        return name

    def edit_lang(self, id):
        id = actions.get_count(self.url, 'languages', self.token)
        trans = '{"DE-de": "lang_de", "ru": "lang_ru"}'
        res = contract.edit_lang(self.url,
                                 self.pr_key,
                                 self.token,
                                 id,
                                 trans)
        self.log.debug(res)
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def test_rollback1(self):
        self.log.info('Start rollback test')
        # Install apps
        actions.imp_app('system', self.url, self.pr_key, self.token, self.l_data['account'])
        actions.imp_app('basic', self.url, self.pr_key, self.token, self.l_data['account'])
        table_name = self.add_user_table()
        self.insert_to_user_table(table_name)
        # Save to file block id for rollback
        rollback_block_id = actions.get_max_block_id(self.url, self.token)
        file = os.path.join(os.getcwd(), 'blockId.txt')
        with open(file, 'w') as f:
            f.write(str(rollback_block_id))
        # Save to file user table name
        table_name_with_prefix = '1_' + table_name
        file = os.path.join(os.getcwd(), 'userTableName.txt')
        with open(file, 'w') as f:
            f.write(table_name_with_prefix)
        # Save to file user table state
        db_user_table_info = db.get_user_table_state(
            self.db_node, table_name_with_prefix)
        file = os.path.join(os.getcwd(), 'dbUserTableState.json')
        with open(file, 'w') as fconf:
            json.dump(db_user_table_info, fconf)
        # Save to file all tables state
        db_information = actions.get_count_DB_objects(self.url, self.token)
        file = os.path.join(os.getcwd(), 'dbState.json')
        with open(file, 'w') as fconf:
            json.dump(db_information, fconf)
        self.insert_to_user_table(table_name)
        self.update_user_table(table_name)
        self.create_ecosystem()
        self.add_notification()
        self.add_binary()
        cont, code = self.create_empty_contract()
        self.edit_contract(cont, code)
        param = self.new_parameter()
        self.edit_parameter(param)
        menu = self.new_menu()
        self.edit_menu(menu)
        self.append_memu(menu)
        page = self.new_page()
        self.edit_page(page)
        self.append_page(page)
        block = self.new_block()
        self.edit_block(block)
        table = self.new_table()
        self.edit_table(table)
        column = self.new_column(table)
        self.edit_column(table, column)
        lang = self.new_lang()
        self.edit_lang(lang)
        actions.imp_app('conditions', self.url, self.pr_key, self.token, self.l_data['account'])
        self.log.info('End rollback test')
