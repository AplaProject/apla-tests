import unittest
import time
from libs import tools, check, actions, db, contract


class TestSecurity(unittest.TestCase):
    config = tools.read_config('nodes')

    def test_change_info_block(self):
        unit = unittest.TestCase()
        db.increase_blocks(self.config[2]['db'])
        unit.assertFalse(check.is_updating(self.config[0]['url']), 'Node ' +\
                        self.config[0]['url'] + ' is updating') 
        unit.assertFalse(check.is_updating(self.config[2]['url']), 'Node ' +\
                        self.config[2]['url'] + ' is updating')
        ts_count = 30
        i = 1
        data = actions.login(self.config[0]['url'], self.config[0]['private_key'], 0)
        token = data['jwtToken']
        amounts_b = actions.get_user_token_amounts(self.config[0]['url'], token)
        while i < ts_count:
            tx_cont = contract.new_contract(self.config[0]['url'],
                                            self.config[0]['private_key'],
                                            token)
            i = i + 1
            time.sleep(1)
        time.sleep(120)
        res = db.compare_node_positions(self.config[0]['db'],
                                  actions.get_max_block_id(self.config[0]['url'], token), 2)
        unit.assertTrue(res, "Inorrect noddes position")
        
    def test_change_hashes(self):
        ts_count = 30
        unit = unittest.TestCase()
        
        data = actions.login(self.config[0]['url'], self.config[0]['private_key'], 0)
        token = data['jwtToken']
        amounts_b = actions.get_user_token_amounts(self.config[0]['url'], token)
        i = 1
        while i < ts_count:
            tx_cont = contract.new_contract(self.config[0]['url'],
                                            self.config[0]['private_key'],
                                            token)
            i = i + 1
            time.sleep(1)
        db.change_hash_block_chain(self.config[2]['db'])
        db.change_hash_info_block(self.config[2]['db'])
        i = 1
        while i < ts_count:
            tx_cont = contract.new_contract(self.config[0]['url'],
                                            self.config[0]['private_key'],
                                            token)
            i = i + 1
            time.sleep(1)
        time.sleep(120)
        
    def test_change_content(self):
        wait = tools.read_config('test')['wait_tx_status']
        conf = tools.read_config('nodes')
        url = conf[0]['url']
        pr_key1 = conf[0]['private_key']
        data = actions.login(url, pr_key1, 0)
        token1 = data['jwtToken']
        actions.imp_app('apla_test_app', url, pr_key1, token1)
        data = {'greeting': 'record1'}
        res = actions.call_contract(url, pr_key1, 'testInsert', data, token1)
        result = actions.tx_status(url, wait, res, token1)
        db.change_content(self.config[2]['db'])
        data1 = {'id': '1'}
        res = actions.call_contract(url, pr_key1, 'testUpdate', data1 , token1)
        result = actions.tx_status(url, wait, res, token1)
        data2 = {'greeting': 'record2'}
        res = actions.call_contract(url, pr_key1, 'testInsert', data2, token1)
        
        
        
        
        


if __name__ == '__main__':
    unittest.main()
