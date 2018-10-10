import unittest
import time
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from libs import tools, actions, db


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
            node_balance.append(db.get_balance_from_db(self.conf[0]["db"],
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
        is_node_commission = db.is_commission_in_history(self.conf[0]["db"], id_from,
                                                       self.conf[node]["keyID"],
                                                       node_commision)
        is_platform_commission = db.is_commission_in_history(self.conf[0]["db"], id_from,
                                                           self.conf[0]["keyID"],
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
        sums_before = db.get_user_token_amounts(self.conf[0]["db"])
        summ_before = sum(summ[0] for summ in sums_before)
        b_node_balance = self.get_node_balances()
        token_runner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pub_runner = get_public_key(self.keys["key2"])
        balance_runner_b = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 1}, token_runner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]["db"], result["blockid"])
        sums_after = db.get_user_token_amounts(self.conf[0]["db"])
        summ_after = sum(summ[0] for summ in sums_after)
        a_node_balance = self.get_node_balances()
        node_commission = 141620000000000000
        platforma_commission = 4380000000000000
        balance_runner_a = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        balance_contract_owner_a = db.get_balance_from_db(self.conf[0]["db"], wallet_id)
        in_history = self.is_commissions_in_history(node_commission, self.conf[0]["keyID"],
                                                   platforma_commission, node)
        if node == 0:
            dict_valid = dict(balanceRunner=balance_runner_a,
                             platformBalance=a_node_balance[0],
                             summ=summ_before,
                             history=in_history)
            dict_expect = dict(balanceRunner=balance_runner_b,
                              platformBalance=a_node_balance[0],
                              summ=summ_before,
                              history=True)
        else:
            dict_valid = dict(balanceRunner=balance_runner_a,
                             platformBalance=a_node_balance[0],
                             nodeBalance=a_node_balance[node],
                             summ=summ_before,
                             history=in_history)
            dict_expect = dict(balanceRunner=balance_runner_b,
                              platformBalance=b_node_balance[0] - node_commission,
                              nodeBalance=b_node_balance[node] + node_commission,
                              summ=summ_after,
                              history=True)
        self.u.assertDictEqual(dict_valid, dict_expect,
                                          "Error in comissions run activated contract")


    def test_deactive_contract(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == True:
            self.deactivate_contract()
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"],
                                                "CostContract", self.token)
        sums_before = db.get_user_token_amounts(self.conf[0]["db"])
        summ_before = sum(summ[0] for summ in sums_before)
        b_node_balance = self.get_node_balances()
        token_runner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pub_runner = get_public_key(self.keys["key2"])
        balance_runner_b = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 1}, token_runner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]["db"], result["blockid"])
        sums_after = db.get_user_token_amounts(self.conf[0]["db"])
        summ_after = sum(summ[0] for summ in sums_after)
        a_node_balance = self.get_node_balances()
        node_commission = 141620000000000000
        platform_commission = 4380000000000000
        commission = node_commission + platform_commission
        balance_runner_a = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        balance_contract_owner_a = db.get_balance_from_db(self.conf[0]["db"], wallet_id)
        in_history = self.is_commissions_in_history(node_commission, data_runner["key_id"],
                                                   platform_commission, node)
        if node == 0:
            dict_valid = dict(balanceRunner=balance_runner_a,
                             platformBalance=a_node_balance[0],
                             summ=summ_before,
                             history=in_history)
            dict_expect = dict(balanceRunner=balance_runner_b - commission,
                              platformBalance=b_node_balance[0] + commission,
                              summ=summ_after,
                              history=True)
        else:
            dict_valid = dict(balanceRunner=balance_runner_a,
                             platformBalance=a_node_balance[0],
                             nodeBalance=a_node_balance[node],
                             summ=summ_before,
                             history=in_history)
            dict_expect = dict(balanceRunner=balance_runner_b - commission,
                              platformBalance=b_node_balance[0] + platform_commission,
                              nodeBalance=b_node_balance[node] + node_commission,
                              summ=summ_after,
                              history=True)
        self.u.assertDictEqual(dict_valid, dict_expect,
                             "Error in comissions run deactivated contract")

    def test_activated_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == False:
            self.activate_contract()
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"], "CostContract", self.token)
        balance_contract_owner_b = db.get_balance_from_db(self.conf[0]["db"], wallet_id)
        balance_node_owner_b = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        commision_wallet = db.get_commission_wallet(self.conf[0]["db"], 1)
        balance_commision_b = db.get_balance_from_db(self.conf[0]["db"], commision_wallet)
        token_runner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pub_runner = get_public_key(self.keys["key2"])
        balance_runner_b = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 0}, token_runner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        time.sleep(10)
        balance_contract_owner_a = db.get_balance_from_db(self.conf[0]["db"], wallet_id)
        balance_node_owner_a = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        balance_commision_a = db.get_balance_from_db(self.conf[0]["db"], commision_wallet)
        balance_runner_a = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        dict_valid = dict(balanceContractOwner=balance_contract_owner_a,
                         balanceNodeOwner=balance_node_owner_a,
                         balanceCommision=balance_commision_a,
                         balanceRunner=balance_runner_a)
        dict_expect = dict(balanceContractOwner=balance_contract_owner_b,
                          balanceNodeOwner=balance_node_owner_b,
                          balanceCommision=balance_commision_b,
                          balanceRunner=balance_runner_b)
        msg = "balance_contract_owner_a:" + str(balance_contract_owner_a) + "\n" + \
              "balanceContractOwnerE:" + str(balance_contract_owner_b) + "\n" + \
              "balance_node_owner_a:" + str(balance_node_owner_a) + "\n" + \
              "balanceNodeOwnerE:" + str(balance_node_owner_b) + "\n" + \
              "balance_commision_a:" + str(balance_commision_a) + "\n" + \
              "balanceCommisionE:" + str(balance_commision_b) + "\n" + \
              "balance_runner_a:" + str(balance_runner_a) + "\n" + \
              "balanceRunnerE:" + str(balance_runner_b) + "\n"
        self.u.assertDictEqual(dict_valid, dict_expect, msg)

    def test_deactive_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == True:
            self.deactivate_contract()
        wallet_id = actions.get_activated_wallet(self.conf[1]["url"], "CostContract", self.token)
        balance_contract_owner_b = db.get_balance_from_db(self.conf[0]["db"], wallet_id)
        balance_node_owner_b = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        commision_wallet = db.get_commission_wallet(self.conf[0]["db"], 1)
        balance_commision_b = db.get_balance_from_db(self.conf[0]["db"], commision_wallet)
        commission = db.get_system_parameter(self.conf[0]["db"], "commission_size")
        token_runner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pub_runner = get_public_key(self.keys["key2"])
        balance_runner_b = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
        data_runner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        token_runner = data_runner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 0}, token_runner)
        time.sleep(10)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res, token_runner)
        balance_contract_owner_a = db.get_balance_from_db(self.conf[0]["db"], wallet_id)
        balance_node_owner_a = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        balance_commision_a = db.get_balance_from_db(self.conf[0]["db"], commision_wallet)
        balance_runner_a = db.get_balance_from_db_by_pub(self.conf[0]["db"], pub_runner)
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