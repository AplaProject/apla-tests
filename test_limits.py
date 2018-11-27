import unittest

from libs import actions, tools, contract, check


MAX_TX_SIZE = 'max_tx_size'
MAX_BLOCK_SIZE = 'max_block_size'
MAX_TX_BLOCK_PER_USER = 'max_tx_block_per_user'
MAX_TX_BLOCK = 'max_tx_block'


class TestLimits():
    conf = tools.read_config('nodes')
    url = conf[1]['url']
    pr_key = conf[0]['private_key']
    contracts = tools.read_fixtures_yaml('contracts')
    wait = tools.read_config('test')['wait_tx_status']
    data = actions.login(url, pr_key, 0)
    token = data['jwtToken']

    def setup_class(self):
        self.unit = unittest.TestCase()
        value = self.contracts['UpdateSysParam_mock']['code']
        self.update_contract_UpdateSysParam(self, value)
        #self.set_default_params_value(self)

    def teardown_class(self):
        #self.set_default_params_value(self)
        value = self.contracts['UpdateSysParam_original']['code']
        self.update_contract_UpdateSysParam(self, value)

    def set_default_params_value(self):
        self.update_sys_param(self, MAX_TX_SIZE, '33554432')
        self.update_sys_param(self, MAX_BLOCK_SIZE, '67108864')
        self.update_sys_param(self, MAX_TX_BLOCK_PER_USER, '100')
        self.update_sys_param(self, MAX_TX_BLOCK, '1000')

    def update_contract_UpdateSysParam(self, value):
        id = actions.get_object_id(self.url,
                                   'UpdateSysParam',
                                   'contracts',
                                   self.token)
        res = contract.edit_contract(self.url,
                                     self.pr_key,
                                     self.token,
                                     id=id,
                                     new_source=value,
                                     condition='ContractConditions("@1DeveloperCondition")')
        check.is_tx_in_block(self.url, self.wait, res, self.token)

    def update_sys_param(self, param, value):
        data = {'Name': param,
                'Value': value}
        res = actions.call_contract(self.url,
                                    self.pr_key,
                                    'UpdateSysParam',
                                    data,
                                    self.token)
        wait = self.wait + 60
        check.is_tx_in_block(self.url,
                             wait,
                             {'hash': res},
                             self.token)

    def test_max_tx_size(self):
        default_param_value = actions.get_sysparams_value(self.url,
                                                          self.token,
                                                          MAX_TX_SIZE)
        self.update_sys_param(MAX_TX_SIZE, '500')
        tx = contract.new_contract(self.url,
                                   self.pr_key,
                                   self.token,
                                   source=self.contracts['limits']['code'])
        msg = 'The size of tx is too big'
        self.unit.assertIn(msg, tx['hash']['msg'],
                           'Incorrect error: ' + str(tx))
        self.update_sys_param(MAX_TX_SIZE, str(default_param_value))

    def test_max_block_size(self):
        default_param_value = actions.get_sysparams_value(self.url,
                                                     self.token,
                                                     MAX_BLOCK_SIZE)
        self.update_sys_param(MAX_BLOCK_SIZE, '500')
        tx = contract.new_contract(self.url,
                                   self.pr_key,
                                   self.token,
                                   source=self.contracts['limits']['code'])
        res = actions.tx_status(self.url,
                             self.wait,
                             tx['hash'],
                             self.token)
        msg = 'stop generating block'
        self.unit.assertEqual(msg, res['error'],
                           'Incorrect error: ' + str(res))
        self.update_sys_param(MAX_BLOCK_SIZE, str(default_param_value))

    def test_max_tx_block_per_user(self):
        count_tx = 1
        default_param_value = actions.get_sysparams_value(self.url,
                                                          self.token,
                                                          MAX_TX_BLOCK_PER_USER)
        self.update_sys_param(MAX_TX_BLOCK_PER_USER, str(count_tx))
        max_block = actions.get_max_block_id(self.url, self.token)
        print('max_block = ' + str(max_block))
        i = 1
        while i < 7:
            tx = contract.new_contract(self.url,
                                       self.pr_key,
                                       self.token,
                                       source=self.contracts['limits']['code'])
            i = i + 1
        max_block = actions.get_max_block_id(self.url, self.token)
        print('max_block = ' + str(max_block))
        self.update_sys_param(MAX_TX_BLOCK_PER_USER, str(default_param_value))
        is_one_or_two = actions.is_count_tx_in_block(self.url,
                                                     self.token,
                                                     max_block,
                                                     count_tx)
        self.unit.assertTrue(is_one_or_two,
                             'One of block contains more than {} transaction'.format(count_tx))

    def test_max_tx_block(self):
        count_tx = 2
        max_tx_block = actions.get_sysparams_value(self.url,
                                                   self.token,
                                                   MAX_TX_BLOCK)
        self.update_sys_param(MAX_TX_BLOCK, str(count_tx))
        max_block = actions.get_max_block_id(self.url, self.token)
        print('max_block = ' + str(max_block))
        i = 1
        while i < 7:
            tx = contract.new_contract(self.url,
                                       self.pr_key,
                                       self.token,
                                       source=self.contracts['limits']['code'])
            i = i + 1
        max_block = actions.get_max_block_id(self.url, self.token)
        print('max_block = ' + str(max_block))
        self.update_sys_param(MAX_TX_BLOCK, str(max_tx_block))
        current_tx_in_block = actions.is_count_tx_in_block(self.url,
                                                           self.token,
                                                           max_block,
                                                           count_tx)
        self.unit.assertTrue(current_tx_in_block,
                             'One of block contains more than {} transaction'.format(count_tx))


    def test_z_default_values(self):
        actual = {
            MAX_TX_SIZE: '33554432',
            MAX_BLOCK_SIZE: '67108864',
            MAX_TX_BLOCK_PER_USER: '100',
            MAX_TX_BLOCK: '1000'
        }
        expected = {
            MAX_TX_SIZE: str(actions.get_sysparams_value(self.url,
                                                         self.token,
                                                         MAX_TX_SIZE)),
            MAX_BLOCK_SIZE: str(actions.get_sysparams_value(self.url,
                                                            self.token,
                                                            MAX_BLOCK_SIZE)),
            MAX_TX_BLOCK_PER_USER: str(actions.get_sysparams_value(self.url,
                                                                   self.token,
                                                                   MAX_TX_BLOCK_PER_USER)),
            MAX_TX_BLOCK: str(actions.get_sysparams_value(self.url,
                                                          self.token,
                                                          MAX_TX_BLOCK))
        }
        self.unit.assertDictEqual(actual, expected, 'Params has not default values')

