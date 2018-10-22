import unittest
import time
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from libs import tools, actions, db
from asyncio.proactor_events import BaseProactorEventLoop

NODE_COMISSION = 139680000000000000
PLATFORM_COMISSION = 4320000000000000

class TestCost():
    wait = tools.read_config("test")["wait_tx_status"]
    conf = tools.read_config("nodes")
    keys = tools.read_fixtures("keys")

    def setup_class(self):
        print("setup_class")
        self.u = unittest.TestCase()
        print("setup_class finished")
        TestCost.create_contracts()

    def setup(self):
        print("setup")
        self.data = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        self.token = self.data["jwtToken"]

    def get_node_balances(self):
        node_count = len(self.conf)
        i = 0
        node_balance = []
        while i < node_count:
            node_balance.append(actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                     self.conf[i]["keyID"]))
            i += 1
        return node_balance

    @staticmethod
    def create_contracts():
        data_creater = actions.login(TestCost.conf[0]["url"], TestCost.conf[0]["private_key"], 0)
        token_creater = data_creater["jwtToken"]
        contract = tools.read_fixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        print("wait: ", TestCost.wait)
        result = actions.call_contract(TestCost.conf[0]["url"], TestCost.conf[0]["private_key"],
                                       "NewContract", data, token_creater)
        status = actions.tx_status(TestCost.conf[0]["url"], TestCost.wait,
                                   result, token_creater)

    def activate_contract(self):
        data_creater = actions.login(self.conf[1]["url"], self.conf[0]["private_key"], 0)
        token_creater = data_creater["jwtToken"]
        id = actions.get_contract_id(self.conf[1]["url"], "CostContract", token_creater)
        data = {"Id": id}
        result = actions.call_contract(self.conf[1]["url"], self.conf[0]["private_key"],
                                       "ActivateContract", data, token_creater)

        status = actions.tx_status(self.conf[1]["url"], self.wait,
                                   result, token_creater)

    def deactivate_contract(self):
        data_creater = actions.login(self.conf[0]["url"], self.conf[0]["private_key"], 0)
        token_creater = data_creater["jwtToken"]
        id = actions.get_contract_id(self.conf[0]["url"], "CostContract", token_creater)
        data = {"Id": id}
        result = actions.call_contract(self.conf[0]["url"], self.conf[0]["private_key"],
                                       "DeactivateContract", data, token_creater)
        status = actions.tx_status(self.conf[0]["url"], self.wait, result, token_creater)

    def is_commissions_in_history(self, node_commision, id_from, platform_commission, node):
        is_node_commission = actions.is_commission_in_history(self.conf[1]["url"], self.token,
                                                         id_from, self.conf[node]["keyID"],
                                                       node_commision)
        is_platform_commission = actions.is_commission_in_history(self.conf[1]["url"], self.token,
                                                             id_from, self.conf[0]["keyID"],
                                                           platform_commission)
        if is_node_commission and is_platform_commission:
            return True
        else:
            return False

    def test_activated_contract(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == False:
            self.activate_contract()
        time.sleep(10)
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"],
                                                "CostContract", self.token)
        summ_before = sum(actions.get_user_token_amounts(self.conf[1]["url"], self.token))
        b_node_balance = self.get_node_balances()
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        balance_runner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                 data_runner['key_id'])
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 1}, token_runner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]["db"], result["blockid"])
        summ_after = sum(actions.get_user_token_amounts(self.conf[1]["url"], self.token))
        a_node_balance = self.get_node_balances()
        balance_runner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                 data_runner['key_id'])
        print('wallet_id', wallet_id)
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                        wallet_id)
        node_commission = NODE_COMISSION
        platforma_commission = PLATFORM_COMISSION
        in_history = self.is_commissions_in_history(node_commission, self.conf[0]["keyID"],
                                                   platforma_commission, node)
        if node == 0:
            dict_valid = dict(balanceRunner=int(balance_runner_a),
                             platformBalance=int(a_node_balance[0]),
                             summ=int(summ_after),
                             history=in_history)
            dict_expect = dict(balanceRunner=int(balance_runner_b),
                              platformBalance=int(a_node_balance[0]),
                              summ=int(summ_before),
                              history=True)
        else:
            dict_valid = dict(balanceRunner=int(balance_runner_a),
                             platformBalance=int(a_node_balance[0]),
                             nodeBalance=int(a_node_balance[node]),
                             summ=int(summ_before),
                             history=in_history)
            dict_expect = dict(balanceRunner=int(balance_runner_b),
                              platformBalance=int(b_node_balance[0]) - int(node_commission),
                              nodeBalance=int(b_node_balance[node]) + int(node_commission),
                              summ=int(summ_after),
                              history=True)
        self.u.assertDictEqual(dict_valid, dict_expect,
                                          "Error in comissions run activated contract")


    def test_deactive_contract(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == True:
            self.deactivate_contract()
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"],
                                                "CostContract", self.token)
        summ_before = sum(actions.get_user_token_amounts(self.conf[1]["url"], self.token))
        b_node_balance = self.get_node_balances()
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        balance_runner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                data_runner['key_id'])
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 1}, token_runner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]["db"], result["blockid"])
        summ_after = sum(actions.get_user_token_amounts(self.conf[1]["url"], self.token))
        a_node_balance = self.get_node_balances()
        node_commission = NODE_COMISSION
        platforma_commission = PLATFORM_COMISSION
        commission = node_commission + platforma_commission
        balance_runner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                data_runner['key_id'])
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                        wallet_id)
        in_history = self.is_commissions_in_history(node_commission, data_runner["key_id"],
                                                   platforma_commission, node)
        if node == 0:
            dict_valid = {'balanceRunner': int(balance_runner_a),
                          'platformBalance': int(a_node_balance[0]), 'summ': int(summ_before),
                          'history': in_history}
            dict_expect = {'balanceRunner': int(balance_runner_b) - int(commission),
                           'platformBalance': int(b_node_balance[0]) + int(commission),
                           'summ': int(summ_after), 'history': True}
        else:
            dict_valid = {'balanceRunner': int(balance_runner_a),
                          'platformBalance': int(a_node_balance[0]), 
                          'nodeBalance': int(a_node_balance[node]), 'summ': int(summ_before),
                          'history': in_history}
            dict_expect = {'balanceRunner': int(balance_runner_b) - int(commission),
                           'platformBalance': int(b_node_balance[0]) + int(platforma_commission),
                           'nodeBalance': int(b_node_balance[node]) + int(node_commission),
                           'summ': int(summ_after), 'history': True}
        self.u.assertDictEqual(dict_valid, dict_expect,
                             "Error in comissions run deactivated contract")

    def test_activated_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == False:
            self.activate_contract()
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"], "CostContract",
                                                 self.token)
        balance_contract_owner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                        wallet_id)
        balance_node_owner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                    self.conf[1]["keyID"])
        commision_wallet = actions.get_sysparam_value(self.conf[1]["url"], self.token,
                                                      'commission_wallet')
        balance_commision_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                   commision_wallet)
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        balance_runner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                 data_runner['key_id'])
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 0}, token_runner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        time.sleep(10)
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                        wallet_id)
        balance_node_owner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                    self.conf[1]["keyID"])
        balance_commision_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                     commision_wallet)
        balance_runner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                 data_runner['key_id'])
        dict_valid = dict(balanceContractOwner=balance_contract_owner_a,
                         balanceNodeOwner=balance_node_owner_a,
                         balanceCommision=balance_commision_a,
                         balanceRunner=balance_runner_a)
        dict_expect = dict(balanceContractOwner=balance_contract_owner_b,
                          balanceNodeOwner=balance_node_owner_b,
                          balanceCommision=balance_commision_b,
                          balanceRunner=balance_runner_b)
        self.u.assertDictEqual(dict_valid, dict_expect, "Error in test_activated_contract_with_err")

    def test_deactive_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == True:
            self.deactivate_contract()
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"], "CostContract", self.token)
        balance_contract_owner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                        wallet_id)
        balance_node_owner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                    self.conf[1]["keyID"])
        commision_wallet = actions.get_sysparam_value(self.conf[1]["url"], self.token, 'commission_wallet')
        balance_commision_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                   commision_wallet)
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        balance_runner_b = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                data_runner['key_id'])
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 0}, token_runner)
        time.sleep(10)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                        wallet_id)
        balance_node_owner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                    self.conf[1]["keyID"])
        balance_commision_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                   commision_wallet)
        balance_runner_a = actions.get_balance_by_id(self.conf[1]["url"], self.token,
                                                 data_runner['key_id'])
        dict_valid = dict(balanceContractOwner = balance_contract_owner_a,
                         balanceNodeOwner = balance_node_owner_a,
                         balanceCommision = balance_commision_a,
                         balanceRunner = balance_runner_a)
        dict_expect = dict(balanceContractOwner = balance_contract_owner_b,
                          balanceNodeOwner = balance_node_owner_b,
                          balanceCommision = balance_commision_b,
                          balanceRunner = balance_runner_b)
        msg = "balance_contract_owner_a:" + str(balance_contract_owner_a) + "\n" +\
        "balanceContractOwnerE:" + str(balance_contract_owner_b) + "\n" +\
        "balance_node_owner_a:" + str(balance_node_owner_a) + "\n" +\
        "balanceNodeOwnerE:" + str(balance_node_owner_b) + "\n" +\
        "balance_commision_a:" + str(balance_commision_a) + "\n" +\
        "balanceCommisionE:" + str(balance_commision_b) + "\n" +\
        "balance_runner_a:" + str(balance_runner_a) + "\n" +\
        "balanceRunnerE:" + str(balance_runner_b) + "\n"
        self.u.assertDictEqual(dict_valid, dict_expect, msg)