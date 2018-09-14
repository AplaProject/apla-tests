import unittest
import time
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from libs.actions import Actions
from libs.db import Db
from libs.tools import Tools
from asyncio.tasks import wait


class TestCost(unittest.TestCase):

    @classmethod
<<<<<<< HEAD
    def setup_class(self):
        global conf, keys
        conf = config.getNodeConfig()
        keys = config.getKeys()
=======
    def setUpClass(self):
        global conf, keys, wait
        wait = Tools.readConfig("test")["wait_tx_status"]
        conf = Tools.readConfig("nodes")
        keys = Tools.readConfig("keys")
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        self.createContracts(self)
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
    
    def createContracts(self):
        global dataCreater
        dataCreater = Actions.login(conf["1"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        contract = Tools.readFixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        result = Actions.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "NewContract", data, tokenCreater)
<<<<<<< HEAD
        status = Actions.tx_status(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                  result['hash'], tokenCreater)
=======
        status = Actions.txstatus(conf["1"]["url"], wait, result['hash'], tokenCreater)
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        
    def activateContract(self):
        dataCreater = Actions.login(conf["2"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = Actions.get_contract_id(conf["2"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = Actions.call_contract(conf["2"]["url"], conf["1"]["private_key"],
                                     "ActivateContract", data, tokenCreater)
<<<<<<< HEAD
        status = Actions.tx_status(conf["2"]["url"], conf["1"]["time_wait_tx_in_block"],
                                  result['hash'], tokenCreater)
=======
        status = Actions.txstatus(conf["2"]["url"], wait, result['hash'], tokenCreater)
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        
    def deactivateContract(self):
        dataCreater = Actions.login(conf["1"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = Actions.get_contract_id(conf["1"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = Actions.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "DeactivateContract", data, tokenCreater)
<<<<<<< HEAD
        status = Actions.tx_status(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                  result['hash'], tokenCreater)
            
    def isCommissionsInHistory(self, nodeCommision, idFrom, platformaCommission, node):
        isNodeCommission = Db.isCommissionInHistory(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         idFrom,
                                                         conf[str(node+1)]["keyID"],
                                                         nodeCommision)
        isPlatformCommission = Db.isCommissionInHistory(conf["1"]["dbHost"],
                                                             conf["1"]["dbName"],
                                                             conf["1"]["login"],
                                                             conf["1"] ["pass"],
                                                             idFrom,
=======
        status = Actions.txstatus(conf["1"]["url"], wait, result['hash'], tokenCreater)
            
    def isCommissionsInHistory(self, nodeCommision, idFrom, platformaCommission, node):
        isNodeCommission = Actions.isCommissionInHistory(conf["1"]["db"], idFrom,
                                                         conf[str(node+1)]["keyID"],
                                                         nodeCommision)
        isPlatformCommission = Actions.isCommissionInHistory(conf["1"]["db"], idFrom,
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
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
<<<<<<< HEAD
        sumsBefore = Db.get_user_token_amounts(conf["1"]["dbHost"],
                                               conf["1"]["dbName"],
                                               conf["1"]["login"],
                                               conf["1"] ["pass"])
=======
        sumsBefore = Db.getUserTokenAmounts(conf["1"]["db"])
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner ["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 1}, tokenRunner)
<<<<<<< HEAD
        result = Actions.tx_status(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  res["hash"], tokenRunner)
        time.sleep(10)
        node = Db.get_block_gen_node(conf["1"]["dbHost"], conf["1"]["dbName"],
                                          conf["1"]["login"], conf["1"] ["pass"],
                                          result["blockid"])
        sumsAfter = Db.get_user_token_amounts(conf["1"]["dbHost"],
                                              conf["1"]["dbName"],
                                              conf["1"]["login"],
                                              conf["1"] ["pass"])
=======
        result = Actions.txstatus(conf["2"]["url"], wait, res["hash"], tokenRunner)
        time.sleep(10)
        node = Db.get_block_gen_node(conf["1"]["db"], result["blockid"])
        sumsAfter = Db.getUserTokenAmounts(conf["1"]["db"])
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 144530000000000000
        platformaCommission = 4470000000000000
        balanceRunnerA = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        balanceContractOwnerA = Db.get_balance_from_db(conf["1"]["db"], walletId)
        inHistory = self.isCommissionsInHistory(nodeCommission, conf["1"]["keyID"],
                                                platformaCommission, node)
        if node == 0:
            dictValid = dict(balanceRunner = balanceRunnerA,
                             platformBalance = aNodeBalance[0],
                             summ = summBefore,
                             history = inHistory)
            dictExpect = dict(balanceRunner = balanceRunnerB,
                             platformBalance = aNodeBalance[0],
                             summ = summBefore,
                             history = True)
        else:
            dictValid = dict(balanceRunner = balanceRunnerA,
                             platformBalance = aNodeBalance[0],
                             nodeBalance = aNodeBalance[node],
                             summ = summBefore,
                             history = inHistory)
            dictExpect = dict(balanceRunner = balanceRunnerB,
                             platformBalance = bNodeBalance[0] - nodeCommission,
                             nodeBalance = bNodeBalance[node] + nodeCommission,
                             summ = summAfter,
                             history = True)
        self.assertDictEqual(dictValid, dictExpect,
                             "Error in comissions run activated contract")
        
    def test_deactive_contract(self):
        if Actions.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == True:
            self.deactivateContract()
        walletId = Actions.get_activated_wallet(conf["2"]["url"],
                                              "CostContract", self.token)
<<<<<<< HEAD
        sumsBefore = Db.get_user_token_amounts(conf["1"]["dbHost"],
                                               conf["1"]["dbName"],
                                               conf["1"]["login"],
                                               conf["1"] ["pass"])
=======
        sumsBefore = Actions.getUserTokenAmounts(conf["1"]["db"])
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner ["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 1}, tokenRunner)
<<<<<<< HEAD
        result = Actions.tx_status(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  res["hash"], tokenRunner)
        time.sleep(10)
        node = Db.get_block_gen_node(conf["1"]["dbHost"], conf["1"]["dbName"],
                                          conf["1"]["login"], conf["1"] ["pass"],
                                          result["blockid"])
        sumsAfter = Db.get_user_token_amounts(conf["1"]["dbHost"],
                                              conf["1"]["dbName"],
                                              conf["1"]["login"],
                                              conf["1"] ["pass"])
=======
        result = Actions.txstatus(conf["2"]["url"], wait, res["hash"], tokenRunner)
        time.sleep(10)
        node = Db.get_block_gen_node(conf["1"]["db"], result["blockid"])
        sumsAfter = Db.getUserTokenAmounts(conf["1"]["db"])
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 144530000000000000
        platformaCommission = 4470000000000000
        commission = nodeCommission + platformaCommission
        balanceRunnerA = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        balanceContractOwnerA = Db.get_balance_from_db(conf["1"]["db"], walletId)
        inHistory = self.isCommissionsInHistory(nodeCommission, dataRunner["key_id"],
                                                platformaCommission, node)
        if node == 0:
            dictValid = dict(balanceRunner = balanceRunnerA,
                             platformBalance = aNodeBalance[0],
                             summ = summBefore,
                             history = inHistory)
            dictExpect = dict(balanceRunner = balanceRunnerB - commission,
                             platformBalance = bNodeBalance[0] + commission,
                             summ = summAfter,
                             history = True)
        else:
            dictValid = dict(balanceRunner = balanceRunnerA,
                             platformBalance = aNodeBalance[0],
                             nodeBalance = aNodeBalance[node],
                             summ = summBefore,
                             history = inHistory)
            dictExpect = dict(balanceRunner = balanceRunnerB - commission,
                             platformBalance = bNodeBalance[0] + platformaCommission,
                             nodeBalance = bNodeBalance[node] + nodeCommission,
                             summ = summAfter,
                             history = True)
        self.assertDictEqual(dictValid, dictExpect,
                             "Error in comissions run deactivated contract")
        
    def test_activated_contract_with_err(self):
        if Actions.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == False:
            self.activateContract()
        walletId = Actions.get_activated_wallet(conf["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = Db.get_balance_from_db(conf["1"]["db"], walletId)
        balanceNodeOwnerB = Db.get_balance_from_db(conf["1"]["db"], conf["2"]["keyID"])
        commisionWallet = Db.get_commission_wallet(conf["1"]["db"], 1)
        balanceCommisionB = Db.get_balance_from_db(conf["1"]["db"], commisionWallet)
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner ["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 0}, tokenRunner)
        hash = res["hash"]
<<<<<<< HEAD
        result = Actions.tx_status(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  hash, tokenRunner)
=======
        result = Actions.txstatus(conf["2"]["url"], wait, hash, tokenRunner)
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        time.sleep(10)
        balanceContractOwnerA = Db.get_balance_from_db(conf["1"]["db"], walletId)
        balanceNodeOwnerA = Db.get_balance_from_db(conf["1"]["db"], conf["2"]["keyID"])
        balanceCommisionA = Db.get_balance_from_db(conf["1"]["db"], commisionWallet)
        balanceRunnerA = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
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
        self.assertDictEqual(dictValid, dictExpect, msg)
        
    def test_deactive_contract_with_err(self):
        if Actions.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == True:
            self.deactivateContract()
        walletId = Actions.get_activated_wallet(conf["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = Db.get_balance_from_db(conf["1"]["db"], walletId)
        balanceNodeOwnerB = Db.get_balance_from_db(conf["1"]["db"], conf["2"]["keyID"])
        commisionWallet = Db.get_commission_wallet(conf["1"]["db"], 1)
        balanceCommisionB = Db.get_balance_from_db(conf["1"]["db"], commisionWallet)
        commission = Db.get_system_parameter(conf["1"]["db"], "commission_size")
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner ["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 0}, tokenRunner)
        time.sleep(10)
        hash = res["hash"]
<<<<<<< HEAD
        result = Actions.tx_status(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  hash, tokenRunner)
        balanceContractOwnerA = Db.get_balance_from_db(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            walletId)
        balanceNodeOwnerA = Db.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        conf["2"]["keyID"])
        balanceCommisionA = Db.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        commisionWallet)
        balanceRunnerA = Db.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            pubRunner)
=======
        result = Actions.txstatus(conf["2"]["url"], wait, hash, tokenRunner)
        balanceContractOwnerA = Db.get_balance_from_db(conf["1"]["db"], walletId)
        balanceNodeOwnerA = Db.get_balance_from_db(conf["1"]["db"], conf["2"]["keyID"])
        balanceCommisionA = Db.get_balance_from_db(conf["1"]["db"], commisionWallet)
        balanceRunnerA = Db.get_balance_from_db_by_pub(conf["1"]["db"], pubRunner)
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
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
        self.assertDictEqual(dictValid, dictExpect, msg)
