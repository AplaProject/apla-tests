import unittest
import time
from builtins import sum

from libs import actions, tools, check, contract


class TestBlockChain():
    full_config = tools.read_config('nodes')
    nodes = len(full_config)
    config1 = full_config[0]
    config2 = full_config[1]
    wait = tools.read_config('test')['wait_tx_status']

    def setup_class(self):
        self.uni = unittest.TestCase()
        data = actions.login(
            self.config1['url'], self.config1['private_key'], 0)
        self.token = data['jwtToken']

    def test_block_chain(self):
        ts_count = 30
        i = 1
        amounts_b = actions.get_user_token_amounts(
            self.config1['url'], self.token)
        print('amounts_b', amounts_b)
        sum_amounts_before = sum(amounts_b)
        while i < ts_count:
            tx_cont = contract.new_contract(self.config1['url'],
                                            self.config1['private_key'],
                                            self.token)
            i = i + 1
            time.sleep(1)
        amounts_after = actions.get_user_token_amounts(
            self.config1['url'], self.token)
        expect = {'isTheSameNodes': True, 'isTheSameDB': True,
                  'sumAmounts': sum_amounts_before}
        dict = {'isTheSameNodes': check.compare_nodes(self.full_config),
                'isTheSameDB': check.compare_db(self.full_config, self.config1['url'],
                                                self.token),
                'sumAmounts': sum(amounts_after)}
        self.uni.assertDictEqual(expect, dict, 'Error in test_block_chain')

    def test_block_chain_edit(self):
        ts_count = 100
        tx = contract.new_menu(
            self.config1['url'], self.config1['private_key'], self.token)
        check.is_tx_in_block(self.config1['url'], self.wait, tx, self.token)
        id = actions.get_object_id(
            self.config1['url'], tx['name'], 'menu', self.token)
        i = 1
        amounts_b = actions.get_user_token_amounts(
            self.config1['url'], self.token)
        sum_amounts_before = sum(amounts_b)
        while i < ts_count:
            tx_edit = contract.edit_menu(self.config1['url'],
                                         self.config1['private_key'],
                                         self.token, id)
            i = i + 1
        amounts_after = actions.get_user_token_amounts(
            self.config1['url'], self.token)
        expect = {'isTheSameNodes': True, 'isTheSameDB': True,
                  'sumAmounts': sum_amounts_before}
        dict = {'isTheSameNodes': check.compare_nodes(self.full_config),
                'isTheSameDB': check.compare_db(self.full_config, self.config1['url'],
                                                self.token),
                'sumAmounts': sum(amounts_after)}
        self.uni.assertDictEqual(
            expect, dict, 'Error in test_block_chain_edit')
