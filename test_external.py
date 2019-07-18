import hashlib
import unittest
import time

from libs import actions, db, tools, contract as contracts, check, api, contract


class TestSimvolio():
    contracts = tools.read_fixtures_yaml('contracts')
    wait = tools.read_config('test')['wait_tx_status']
    wait_ex = tools.read_config('test')['wait_external']
    config = tools.read_config('nodes')
    config_ex = tools.read_config('nodes_ex')
    unit = unittest.TestCase()

    def setup(self):
        print('setup class')
        self.url = self.config[1]['url']
        self.pr_key = self.config[0]['private_key']
        self.db1 = self.config[0]['db']
        self.url_ex = self.config_ex[0]['url']
        self.pr_key_ex = self.config_ex[0]['private_key']
        self.db_ex = self.config_ex[0]['db']
        data = actions.login(self.url, self.pr_key, 0)
        self.token = data['jwtToken']
        data_ex = actions.login(self.url_ex, self.pr_key_ex, 0)
        self.token_ex = data_ex['jwtToken']
        
        if not actions.is_contract_present(self.url_ex, self.token_ex, "ExCont"):
            contract_ex = self.contracts['external_cont']['code']
            tx_ex = contracts.new_contract(
                self.url_ex, self.pr_key_ex, self.token_ex, name="ExCont", source=contract_ex)
            check.is_tx_in_block(self.url_ex, self.wait, tx_ex, self.token_ex)
        
        if not actions.is_contract_present(self.url, self.token, "CallExCont"):
            contract_call_ex = self.contracts['call_ex_cont']['code']
            tx_call_ex = contracts.new_contract(
                self.url, self.pr_key, self.token, name="CallExCont", source=contract_call_ex)
            check.is_tx_in_block(self.url, self.wait, tx_call_ex, self.token)
        
        if not actions.is_contract_present(self.url, self.token, "ResCont"):
            contract_res = self.contracts['result_cont']['code']
            tx_res = contracts.new_contract(
                self.url, self.pr_key, self.token, name="ResCont", source=contract_res)
            check.is_tx_in_block(self.url, self.wait, tx_res, self.token)
            
    def wait_for_result(self):
        result = False
        sec = 0
        while sec < self.wait_ex:
            time.sleep(1)
            count = actions.get_count(self.url, "external", self.token)
            print("count: ", count)
            if int(count) > 2:
                result = True
                break
            else:
                sec = sec + 1
        return result
        
        
    def test_external_contract(self):
        tx = contract.new_table(self.url, self.pr_key, self.token, name="external")
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        tx2 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx['name'], type='varchar', name="UID")
        check.is_tx_in_block(self.url, self.wait, tx2, self.token)
        tx3 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx['name'], type='varchar', name="Status")
        check.is_tx_in_block(self.url, self.wait, tx3, self.token)
        tx4 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx['name'], type='varchar', name="Block")
        check.is_tx_in_block(self.url, self.wait, tx4, self.token)
        tx5 = contract.new_column(self.url, self.pr_key, self.token,
                                  tx['name'], type='varchar', name="Msg")
        check.is_tx_in_block(self.url, self.wait, tx5, self.token)
        
        data = {"Url": self.config_ex[0]['api_address'],
                "ResCont": "@1ResCont",
                "ExCont": "@1ExCont"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        
        if self.wait_for_result():
            list = actions.get_list(self.url, 'external', self.token, app_id=0)
            for item in list['list']:
                self.unit.assertEqual(item['uid'], '123456', "Uid is not equal")
                self.unit.assertEqual(item['status'], '0', "Uid is not equal")
                self.unit.assertGreater(int(item['block']), 0, "Block is 0")
        else:
            self.unit.fail("No any results in the table" )
        
        
    def test_external_contract_incorrect_url(self):
        data = {"Url": "tryam",
                "ResCont": "@1ResCont",
                "ExCont": "@1ExCont"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        print(result)
        
    def test_external_contract_incorrect_ex_contract(self):
        data = {"Url": self.config_ex[0]['api_address'],
                "ResCont": "@1ResCont",
                "ExCont": "@1Tryam"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        print(result)
        
    def test_external_contract_incorrect_result_contract(self):
        data = {"Url": self.config_ex[0]['api_address'],
                "ResCont": "@1Tryam",
                "ExCont": "@1ExCont"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        print(result)



