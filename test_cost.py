import unittest
import time
import pytest
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
        TestCost.createContracts()

    def setup(self):
        print("setup")
        self.data = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        self.token = self.data["jwtToken"]

    def getNodeBalances(self):
        nodeCount = len(self.conf)
        i = 0
        nodeBalance = []
        while i < nodeCount:
            nodeBalance.append(db.get_balance_from_db(self.conf[0]["db"],
                                                      self.conf[i]["keyID"]))
            i += 1
        return nodeBalance

    @staticmethod
    def createContracts():
        global dataCreater
        dataCreater = actions.login(TestCost.conf[0]["url"], TestCost.conf[0]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        contract = tools.read_fixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        print("wait: ", TestCost.wait)
        result = actions.call_contract(TestCost.conf[0]["url"], TestCost.conf[0]["private_key"],
                                       "NewContract", data, tokenCreater)
        status = actions.tx_status(TestCost.conf[0]["url"], TestCost.wait,
                                   result['hash'], tokenCreater)

    def activateContract(self):
        dataCreater = actions.login(self.conf[1]["url"], self.conf[0]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = actions.get_contract_id(self.conf[1]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = actions.call_contract(self.conf[1]["url"], self.conf[0]["private_key"],
                                       "ActivateContract", data, tokenCreater)

        status = actions.tx_status(self.conf[1]["url"], self.wait,
                                   result['hash'], tokenCreater)

    def deactivateContract(self):
        dataCreater = actions.login(self.conf[0]["url"], self.conf[0]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = actions.get_contract_id(self.conf[0]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = actions.call_contract(self.conf[0]["url"], self.conf[0]["private_key"],
                                       "DeactivateContract", data, tokenCreater)
        status = actions.tx_status(self.conf[0]["url"], self.wait, result['hash'], tokenCreater)

    def isCommissionsInHistory(self, nodeCommision, idFrom, platformaCommission, node):
        isNodeCommission = db.is_commission_in_history(self.conf[0]["db"], idFrom,
                                                         self.conf[node]["keyID"],
                                                         nodeCommision)
        isPlatformCommission = db.is_commission_in_history(self.conf[0]["db"], idFrom,
                                                             self.conf[0]["keyID"],
                                                             platformaCommission)
        if isNodeCommission and isPlatformCommission:
            return True
        else:
            return False

    def test_activated_contract(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == False:
            self.activateContract()
        time.sleep(10)
        walletId = actions.get_activated_wallet(self.conf[1]["url"],
                                                "CostContract", self.token)
        sumsBefore = db.get_user_token_amounts(self.conf[0]["db"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pubRunner = get_public_key(self.keys["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        dataRunner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 1}, tokenRunner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res["hash"], tokenRunner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]["db"], result["blockid"])
        sumsAfter = db.get_user_token_amounts(self.conf[0]["db"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 141620000000000000
        platformaCommission = 4380000000000000
        balanceRunnerA = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        balanceContractOwnerA = db.get_balance_from_db(self.conf[0]["db"], walletId)
        inHistory = self.isCommissionsInHistory(nodeCommission, self.conf[0]["keyID"],
                                                platformaCommission, node)
        if node == 0:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB,
                              platformBalance=aNodeBalance[0],
                              summ=summBefore,
                              history=True)
        else:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             nodeBalance=aNodeBalance[node],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB,
                              platformBalance=bNodeBalance[0] - nodeCommission,
                              nodeBalance=bNodeBalance[node] + nodeCommission,
                              summ=summAfter,
                              history=True)
        self.u.assertDictEqual(dictValid, dictExpect,
                                          "Error in comissions run activated contract")


    def test_deactive_contract(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == True:
            self.deactivateContract()
        walletId = actions.get_activated_wallet(self.conf[1]["url"],
                                                "CostContract", self.token)
        sumsBefore = db.get_user_token_amounts(self.conf[0]["db"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pubRunner = get_public_key(self.keys["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        dataRunner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 1}, tokenRunner)
        result = actions.tx_status(self.conf[1]["url"], self.wait, res["hash"], tokenRunner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]["db"], result["blockid"])
        sumsAfter = db.get_user_token_amounts(self.conf[0]["db"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 141620000000000000
        platformaCommission = 4380000000000000
        commission = nodeCommission + platformaCommission
        balanceRunnerA = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        balanceContractOwnerA = db.get_balance_from_db(self.conf[0]["db"], walletId)
        inHistory = self.isCommissionsInHistory(nodeCommission, dataRunner["key_id"],
                                                platformaCommission, node)
        if node == 0:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB - commission,
                              platformBalance=bNodeBalance[0] + commission,
                              summ=summAfter,
                              history=True)
        else:
            dictValid = dict(balanceRunner=balanceRunnerA,
                             platformBalance=aNodeBalance[0],
                             nodeBalance=aNodeBalance[node],
                             summ=summBefore,
                             history=inHistory)
            dictExpect = dict(balanceRunner=balanceRunnerB - commission,
                              platformBalance=bNodeBalance[0] + platformaCommission,
                              nodeBalance=bNodeBalance[node] + nodeCommission,
                              summ=summAfter,
                              history=True)
        self.u.assertDictEqual(dictValid, dictExpect,
                             "Error in comissions run deactivated contract")

    def test_activated_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == False:
            self.activateContract()
        walletId = actions.get_activated_wallet(self.conf[1]["url"], "CostContract", self.token)
        balanceContractOwnerB = db.get_balance_from_db(self.conf[0]["db"], walletId)
        balanceNodeOwnerB = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        commisionWallet = db.get_commission_wallet(self.conf[0]["db"], 1)
        balanceCommisionB = db.get_balance_from_db(self.conf[0]["db"], commisionWallet)
        tokenRunner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pubRunner = get_public_key(self.keys["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        dataRunner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 0}, tokenRunner)
        hash = res["hash"]
        result = actions.tx_status(self.conf[1]["url"], self.wait, hash, tokenRunner)
        time.sleep(10)
        balanceContractOwnerA = db.get_balance_from_db(self.conf[0]["db"], walletId)
        balanceNodeOwnerA = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        balanceCommisionA = db.get_balance_from_db(self.conf[0]["db"], commisionWallet)
        balanceRunnerA = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        dictValid = dict(balanceContractOwner=balanceContractOwnerA,
                         balanceNodeOwner=balanceNodeOwnerA,
                         balanceCommision=balanceCommisionA,
                         balanceRunner=balanceRunnerA)
        dictExpect = dict(balanceContractOwner=balanceContractOwnerB,
                          balanceNodeOwner=balanceNodeOwnerB,
                          balanceCommision=balanceCommisionB,
                          balanceRunner=balanceRunnerB)
        msg = "balanceContractOwnerA:" + str(balanceContractOwnerA) + "\n" + \
              "balanceContractOwnerE:" + str(balanceContractOwnerB) + "\n" + \
              "balanceNodeOwnerA:" + str(balanceNodeOwnerA) + "\n" + \
              "balanceNodeOwnerE:" + str(balanceNodeOwnerB) + "\n" + \
              "balanceCommisionA:" + str(balanceCommisionA) + "\n" + \
              "balanceCommisionE:" + str(balanceCommisionB) + "\n" + \
              "balanceRunnerA:" + str(balanceRunnerA) + "\n" + \
              "balanceRunnerE:" + str(balanceRunnerB) + "\n"
        self.u.assertDictEqual(dictValid, dictExpect, msg)

    def test_deactive_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]["url"], "CostContract", self.token) == True:
            self.deactivateContract()
        walletId = actions.get_activated_wallet(self.conf[1]["url"], "CostContract", self.token)
        balanceContractOwnerB = db.get_balance_from_db(self.conf[0]["db"], walletId)
        balanceNodeOwnerB = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        commisionWallet = db.get_commission_wallet(self.conf[0]["db"], 1)
        balanceCommisionB = db.get_balance_from_db(self.conf[0]["db"], commisionWallet)
        commission = db.get_system_parameter(self.conf[0]["db"], "commission_size")
        tokenRunner, uid = actions.get_uid(self.conf[1]["url"])
        signature = sign(self.keys["key2"], uid)
        pubRunner = get_public_key(self.keys["key2"])
        balanceRunnerB = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        dataRunner = actions.login(self.conf[1]["url"], self.keys["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = actions.call_contract(self.conf[1]["url"], self.keys["key2"],
                                    "CostContract", {"State": 0}, tokenRunner)
        time.sleep(10)
        hash = res["hash"]
        result = actions.tx_status(self.conf[1]["url"], self.wait, hash, tokenRunner)
        balanceContractOwnerA = db.get_balance_from_db(self.conf[0]["db"], walletId)
        balanceNodeOwnerA = db.get_balance_from_db(self.conf[0]["db"], self.conf[1]["keyID"])
        balanceCommisionA = db.get_balance_from_db(self.conf[0]["db"], commisionWallet)
        balanceRunnerA = db.get_balance_from_db_by_pub(self.conf[0]["db"], pubRunner)
        dictValid = dict(balanceContractOwner = balanceContractOwnerA,
                         balanceNodeOwner = balanceNodeOwnerA,
                         balanceCommision = balanceCommisionA,
                         balanceRunner = balanceRunnerA)
        dictExpect = dict(balanceContractOwner = balanceContractOwnerB,
                          balanceNodeOwner = balanceNodeOwnerB,
                          balanceCommision = balanceCommisionB,
                          balanceRunner = balanceRunnerB)
        msg = "balanceContractOwnerA:" + str(balanceContractOwnerA) + "\n" +\
        "balanceContractOwnerE:" + str(balanceContractOwnerB) + "\n" +\
        "balanceNodeOwnerA:" + str(balanceNodeOwnerA) + "\n" +\
        "balanceNodeOwnerE:" + str(balanceNodeOwnerB) + "\n" +\
        "balanceCommisionA:" + str(balanceCommisionA) + "\n" +\
        "balanceCommisionE:" + str(balanceCommisionB) + "\n" +\
        "balanceRunnerA:" + str(balanceRunnerA) + "\n" +\
        "balanceRunnerE:" + str(balanceRunnerB) + "\n"
        self.u.assertDictEqual(dictValid, dictExpect, msg)