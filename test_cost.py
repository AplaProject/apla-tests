import unittest
import time
import pytest
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from libs.actions import Actions
from libs.db import Db
from libs.tools import Tools



class TestCost():

    def setup_class(cls):
        print("setup_class")
        global conf, keys, wait
        wait = Tools.read_config("test")["wait_tx_status"]
        conf = Tools.read_config("nodes")
        keys = Tools.read_fixtures("keys")
        print("setup_class finished")
        TestCost.createContracts()

    def setup(self):
        print("setup")
        self.data = Actions.login(conf["2"]["url"], keys["key2"], 0)
        self.token = self.data["jwtToken"]

    def getNodeBalances(self):
        nodeCount = len(conf)
        i = 1
        nodeBalance = []
        while i < nodeCount + 1:
            nodeBalance.append(Db.get_balance_from_db(conf["1"]["db"], conf[str(i)]["keyID"]))
            i = i + 1
        return nodeBalance

    @staticmethod
    def createContracts():
        global dataCreater
        dataCreater = Actions.login(conf["1"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        contract = Tools.read_fixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        print("wait: ", wait)
        result = Actions.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                       "NewContract", data, tokenCreater)
        status = Actions.tx_status(conf["1"]["url"], wait,
                                   result['hash'], tokenCreater)

    def activateContract(self):
        dataCreater = Actions.login(conf["2"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = Actions.get_contract_id(conf["2"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = Actions.call_contract(conf["2"]["url"], conf["1"]["private_key"],
                                       "ActivateContract", data, tokenCreater)

        status = Actions.tx_status(conf["2"]["url"], wait,
                                   result['hash'], tokenCreater)

    def deactivateContract(self):
        dataCreater = Actions.login(conf["1"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = Actions.get_contract_id(conf["1"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = Actions.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                       "DeactivateContract", data, tokenCreater)
        status = Actions.tx_status(conf["1"]["url"], wait, result['hash'], tokenCreater)

    def isCommissionsInHistory(self, nodeCommision, idFrom, platformaCommission, node):
        isNodeCommission = Db.is_commission_in_history(conf["1"]["db"], idFrom,
                                                         conf[str(node + 1)]["keyID"],
                                                         nodeCommision)
        isPlatformCommission = Db.is_commission_in_history(conf["1"]["db"], idFrom,
                                                             conf["1"]["keyID"],
                                                             platformaCommission)
        if isNodeCommission and isPlatformCommission:
            return True
        else:
            return False

    def test_activated_contract(self):
        if Actions.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == False:
            self.activateContract()
        time.sleep(10)
        walletId = Actions.get_activated_wallet(conf["2"]["url"],
                                                "CostContract", self.token)
        sumsBefore = Db.get_user_token_amounts(conf["1"]["db"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                    "CostContract", {"State": 1}, tokenRunner)
        result = Actions.tx_status(conf["2"]["url"], wait, res["hash"], tokenRunner)
        time.sleep(10)
        node = Db.get_block_gen_node(conf["1"]["db"], result["blockid"])
        sumsAfter = Db.get_user_token_amounts(conf["1"]["db"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 144530000000000000
        platformaCommission = 4470000000000000
        balanceRunnerA = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        balanceContractOwnerA = Db.get_balance_from_db(conf["1"]["db"], walletId)
        inHistory = self.isCommissionsInHistory(nodeCommission, conf["1"]["keyID"],
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
        unittest.TestCase().assertDictEqual(dictValid, dictExpect,
                                          "Error in comissions run activated contract")
