import unittest
import json
import time

from libs import actions, tools


class TestLimits():
    conf = tools.read_config('nodes')
    contracts = tools.read_fixtures('contracts')
    wait = tools.read_config('test')['wait_tx_status']
    data = actions.login(conf[1]['url'],
                         conf[0]['private_key'], 0)
    token = data['jwtToken']

    def setup_class(self):
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, result, jwtToken):
        status = actions.tx_status(
            self.conf[1]['url'], self.wait, result, self.token)
        print('status tx: ', status)
        if int(status['blockid']) > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status['blockid']
        else:
            return status['error']

    def call(self, name, data):
        resp = actions.call_contract(self.conf[1]['url'], self.conf[0]['private_key'],
                                     name, data, self.token)
        res = self.assert_tx_in_block(resp, self.token)
        return res

    def update_sys_param(self, param, value):
        data = {'Name': param, 'Value': value}
        res = self.call('UpdateSysParam', data)
        self.unit.assertGreater(int(res), 0,
                                'Block is not generated for updating sysparam: ' +
                                str(res))

    def test_pass(self):
        self.unit.assertGreater(5, 0, 'err')

    def max_tx_size(self):
        max_tx_size = actions.get_sysparams_value(self.conf[1]['url'], self.token,
                                                  'max_tx_size')
        print(max_tx_size)
        self.update_sys_param('max_tx_size', '500')
        name = 'cont' + tools.generate_random_name()
        code = 'contract ' + name + self.contracts['limits']['code']
        data = {'Wallet': '', 'Value': code, 'ApplicationId': 1,
                'Conditions': 'true'}
        error = self.call('NewContract', data)
        self.unit.assertEqual(error, 'Max size of tx',
                              'Incorrect error: ' + error)
        self.update_sys_param('max_tx_size', str(max_tx_size))

    def max_block_size(self):
        max_block_size = actions.get_sysparams_value(
            self.conf[1]['url'], self.token, 'max_block_size')
        self.update_sys_param('max_block_size', '500')
        name = 'cont' + tools.generate_random_name()
        code = 'contract ' + name + self.contracts['limits']['code']
        data = {'Wallet': '', 'Value': code, 'ApplicationId': 1,
                'Conditions': 'true'}
        error = self.call('NewContract', data)
        self.unit.assertEqual(error, 'Max size of tx',
                              'Incorrect error: ' + error)
        self.update_sys_param('max_block_size', str(max_block_size))
        time.sleep(30)

    def max_block_user_tx(self):
        max_block_user_tx = actions.get_sysparams_value(self.conf[1]['url'],
                                                        self.token, 'max_block_user_tx')
        self.update_sys_param('max_block_user_tx', '1')
        time.sleep(30)
        i = 1
        while i < 10:
            name = 'cont' + tools.generate_random_name()
            code = 'contract ' + name + self.contracts['limits']['code']
            data = {'Wallet': '', 'Value': code, 'ApplicationId': 1,
                    'Conditions': 'true'}
            actions.call_contract(self.conf[1]['url'], self.conf[0]['private_key'],
                                  'NewContract', data, self.token)
            i = i + 1
        time.sleep(5)
        max_block = actions.get_max_block_id(self.conf[1]['url'], self.token)
        print('max_block = ', max_block)
        is_one_or_two = actions.is_count_tx_in_block(
            self.conf[1]['url'], self.token, max_block, 1)
        self.update_sys_param('max_block_user_tx ', str(max_block_user_tx))
        time.sleep(30)
        self.unit.assertTrue(is_one_or_two,
                             'One of block contains more than 2 transaction')

    def max_tx_count(self):
        max_tx_count = actions.get_sysparams_value(
            self.conf[0]['url'], self.token, 'max_tx_count')
        self.update_sys_param('max_tx_count', '2')
        i = 1
        while i < 10:
            name = 'cont' + tools.generate_random_name()
            code = 'contract ' + name + self.contracts['limits']['code']
            data = {'Wallet': '', 'Value': code, 'ApplicationId': 1,
                    'Conditions': 'true'}
            actions.call_contract(self.conf[1]['url'], self.conf[0]['private_key'],
                                  'NewContract', data, self.token)
            i = i + 1
        time.sleep(5)
        max_block = actions.get_max_block_id(self.conf[1]['url'], self.token)
        self.unit.assertTrue(actions.is_count_tx_in_block(self.conf[1]['url'], self.token,
                                                          max_block, 2),
                             'One of block contains more than 2 transaction')
        self.update_sys_param('max_tx_count ', str(max_tx_count))
