import unittest
import time
import random
import string

from libs import actions, tools, contract, check, loger


MAX_TX_SIZE = 'max_tx_size'
MAX_BLOCK_SIZE = 'max_block_size'
MAX_TX_BLOCK_PER_USER = 'max_tx_block_per_user'
MAX_TX_BLOCK = 'max_tx_block'
CONT_NAME = 'LimitTest'


class TestLimits():
    UPDATE_SYS_PARAM_VALUE = ''
    conf = tools.read_config('nodes')
    url = conf[1]['url']
    pr_key = conf[0]['private_key']
    contracts = tools.read_fixtures_yaml('contracts')
    wait = tools.read_config('test')['wait_tx_status']
    wait_multi = tools.read_config('test')['wait_tx_status_multi']
    wait_sync = tools.read_config('test')['wait_upating_node']
    data = actions.login(url, pr_key, 0)
    token = data['jwtToken']
    log = loger.create_loger(__name__)
    if not actions.is_contract_present(url, token, CONT_NAME):
        tx = contract.new_contract(url, pr_key, token, source=contracts['limits']['code'],
                                   name=CONT_NAME)
    


    def setup_class(self):
        self.unit = unittest.TestCase()
        # replace contract 'UpdateSysParam' for the mock
        value = self.contracts['UpdateSysParam_mock']['code']
        self.update_contract_UpdateSysParam(self, value)


    def teardown_class(self):
        self.set_default_params_value(self)
        # rollback changes in contract 'UpdateSysParam'
        value = self.contracts['UpdateSysParam_original']['code']
        self.update_contract_UpdateSysParam(self, value)
        
    def generate_param(self, count):
        st = []
        for i in range(1, int(count)):
            for _ in [' abcdefghijklmnopqastuvwxyz']:
                sym = random.choice(string.ascii_lowercase)
                st.append(sym)
        st_s = ''.join(st)
        print("String: ", st_s)
        return st_s

    def assert_multi_tx_in_block(self, result, jwt_token):
        result = actions.tx_status_multi(
            self.url, self.wait_multi, result['hashes'], jwt_token)
        print("Result: ", result)
        for status in result.values():
            self.unit.assertNotIn('errmsg', status)
            print("Status: ", str(status))
            self.unit.assertGreater(
                int(status['blockid']), 0, 'BlockID not generated')
            

    def set_default_params_value(self):
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
        if actual != expected:
            self.log.warning('Run set_default_params_value method')
            self.update_sys_param(self, MAX_TX_SIZE, '33554432')
            self.update_sys_param(self, MAX_BLOCK_SIZE, '67108864')
            self.update_sys_param(self, MAX_TX_BLOCK_PER_USER, '100')
            self.update_sys_param(self, MAX_TX_BLOCK, '1000')
        else:
            self.log.info('Parameters has default values')


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
        check.is_tx_in_block(self.url,
                             self.wait,
                             {'hash': res},
                             self.token)


    def test_max_tx_size(self):
        max_tx_size_value = actions.get_sysparams_value(self.url,
                                                          self.token,
                                                          MAX_TX_SIZE)
        par = self.generate_param(max_tx_size_value)
        data = {'Par': par}
        print(data)
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    CONT_NAME,
                                    data,
                                    self.token)
        print('tx: ', tx)
        msg = 'The size of tx is too big'
        self.unit.assertIn(msg, tx['msg'],
                           'Incorrect error: ' + str(tx))


    def test_max_block_size(self):
        max_block_size = actions.get_sysparams_value(self.url,
                                                     self.token,
                                                     MAX_BLOCK_SIZE)
        max_tx_size = actions.get_sysparams_value(self.url,
                                                     self.token,
                                                     MAX_TX_SIZE)
        new_max_block_size = round(int(max_tx_size)/4)
        param_length = round(int(max_tx_size)/2)
        self.update_sys_param(MAX_BLOCK_SIZE, str(new_max_block_size))
        par = self.generate_param(param_length)
        data = {'Par': par}
        tx = actions.call_contract(self.url, self.pr_key, CONT_NAME,
                                   data, self.token)
        st = actions.tx_status(self.url, self.wait, tx, self.token)
        self.update_sys_param(MAX_BLOCK_SIZE, str(max_block_size))
        msg = 'stop generating block'
        self.unit.assertEqual(msg, st['error'],
                          'Incorrect error: ' + str(tx))

    def test_max_tx_block(self):
        count_tx = 1
        max_tx_block = actions.get_sysparams_value(self.url,
                                                   self.token,
                                                   MAX_TX_BLOCK)
        self.update_sys_param(MAX_TX_BLOCK, str(count_tx))
        
        data = [{'contract': CONT_NAME,
                 'params': {'Par': 'true'}} for _ in range(5)]
        resp = actions.call_multi_contract(self.url, self.pr_key,
                                           CONT_NAME, data,
                                           self.token, False)
        resp = self.assert_multi_tx_in_block(resp, self.token)
        
        if actions.is_sync(self.conf, self.wait_sync, len(self.conf)):
            max_block = actions.get_max_block_id(self.url, self.token)
            self.update_sys_param(MAX_TX_BLOCK, str(max_tx_block))
            current_tx_in_block = actions.is_count_tx_in_block(self.url,
                                                               self.token,
                                                               max_block,
                                                               count_tx)
            self.unit.assertTrue(current_tx_in_block,
                                 'One of block contains more than {} transaction'.format(count_tx))
