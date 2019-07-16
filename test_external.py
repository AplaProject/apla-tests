import hashlib
import unittest
import time

from libs import actions, db, tools, contract as contracts, check, api


class TestSimvolio():
    contracts = tools.read_fixtures_yaml('contracts')
    wait = tools.read_config('test')['wait_tx_status']
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
        
        
    def test_external_contract(self):
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
        data = {"Url": self.config_ex[0]['api_address'],
                "ResCont": "@1ResCont",
                "ExCont": "@1ExCont"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        
    def test_external_contract_incorrect_url(self):
        data = {"Url": "tryam",
                "ResCont": "@1ResCont",
                "ExCont": "@1ExCont"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        
    def test_external_contract_incorrect_ex_contract(self):
        data = {"Url": self.config_ex[0]['api_address'],
                "ResCont": "@1ResCont",
                "ExCont": "@1Tryam"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)
        
    def test_external_contract_incorrect_result_contract(self):
        data = {"Url": self.config_ex[0]['api_address'],
                "ResCont": "@1ResCont",
                "ExCont": "@1ExCont"}
        res = actions.call_contract(
            self.url, self.pr_key, "CallExCont",
            data, self.token)
        result = actions.tx_status(self.url, self.wait, res, self.token)



