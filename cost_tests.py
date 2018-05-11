import unittest
import utils
import config
import json
import time
import funcs
import os


class CostTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global conf, keys
        conf = config.getNodeConfig()
        keys = config.getKeys()
        self.createContracts(self)
        self.createrUsers(self)
        
    def setUp(self):
        self.data = utils.login(conf["2"]["url"],keys["key2"])
        self.token = self.data["jwtToken"]
        
    def getNodeBalances(self):
        nodeCount = len(conf)
        i = 1
        nodeBalance = []
        while i < nodeCount + 1:
            nodeBalance.append(utils.get_balance_from_db(conf["1"]["dbHost"],
                                                    conf["1"]["dbName"],
                                                    conf["1"]["login"],
                                                    conf["1"] ["pass"],
                                                    conf[str(i)]["keyID"]))
            i = i + 1
        return nodeBalance
    
    def createContracts(self):
        global dataCreater
        dataCreater = utils.login(conf["1"]["url"],conf["1"]["private_key"])
        tokenCreater = dataCreater["jwtToken"]
        contract = config.readFixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        result = utils.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "NewContract", data, tokenCreater)
        status = utils.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                result['hash'], tokenCreater)
        code2 = "contract GetKeyId" + contract["get_keyId"]["code"]
        data2 = {"Wallet": "", "Value": code2, "ApplicationId": 1,
                "Conditions": "true"}
        result = utils.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "NewContract", data2, tokenCreater)
        status = utils.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                result['hash'], tokenCreater)
        
    def activateContract(self):
        dataCreater = utils.login(conf["2"]["url"],conf["1"]["private_key"])
        tokenCreater = dataCreater["jwtToken"]
        id = funcs.get_contract_id(conf["2"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = utils.call_contract(conf["2"]["url"], conf["1"]["private_key"],
                                     "ActivateContract", data, tokenCreater)
        status = utils.txstatus(conf["2"]["url"], conf["1"]["time_wait_tx_in_block"],
                                result['hash'], tokenCreater)
        
    def deactivateContract(self):
        dataCreater = utils.login(conf["1"]["url"],conf["1"]["private_key"])
        tokenCreater = dataCreater["jwtToken"]
        id = funcs.get_contract_id(conf["1"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = utils.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "DeactivateContract", data, tokenCreater)
        status = utils.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                result['hash'], tokenCreater) 
        
    def getWalletOwenerBalance(self):
        walletId = funcs.get_activated_wallet(conf["2"]["url"], "CostContract",
                                              self.token)
        return utils.get_balance_from_db(conf["1"]["dbHost"], conf["1"]["dbName"],
                                         conf["1"]["login"], conf["1"] ["pass"],
                                            walletId)
    
    def getComissionWalletBalance(self):
        commisionWallet = utils.get_commission_wallet(conf["1"]["dbHost"],
                                                      conf["1"]["dbName"],
                                                      conf["1"]["login"],
                                                      conf["1"] ["pass"], 1)
        return utils.get_balance_from_db(conf["1"]["dbHost"], conf["1"]["dbName"],
                                         conf["1"]["login"], conf["1"] ["pass"],
                                         commisionWallet)
           
    def createrUsers(self):
        token, uid = utils.get_uid(conf["1"]["url"])
        signature, pubkey1 = utils.sign(uid, conf["1"]["url"], keys["key1"])
        token, uid = utils.get_uid(conf["1"]["url"])
        signature, pubkey2 = utils.sign(uid, conf["1"]["url"], keys["key2"])
        dataKey1 = utils.login(conf["1"]["url"],keys["key1"])
        dataKey2 = utils.login(conf["1"]["url"],keys["key2"])
        dataPlatform = utils.login(conf["1"]["url"],conf["1"]["private_key"])
        tokenPlatform = dataPlatform["jwtToken"]
        data1 = {"Recipient": dataKey1["address"], "Amount": "100000000000000000000"}
        data2 = {"Recipient": dataKey2["address"], "Amount": "100000000000000000000"}
        result = utils.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "MoneyTransfer", data1, tokenPlatform)
        status = utils.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                result['hash'], tokenPlatform) 
        result = utils.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "MoneyTransfer", data2, tokenPlatform)
        status = utils.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                result['hash'], tokenPlatform)
        
    def isCommissionsInHistory(self, nodeCommision, idFrom, platformaCommission, node):
        isNodeCommission = utils.isCommissionInHistory(conf["1"]["dbHost"],
                                                       conf["1"]["dbName"],
                                                       conf["1"]["login"],
                                                       conf["1"] ["pass"],
                                                       idFrom,
                                                       conf[str(node+1)]["keyID"],
                                                       nodeCommision)
        isPlatformCommission = utils.isCommissionInHistory(conf["1"]["dbHost"],
                                                           conf["1"]["dbName"],
                                                           conf["1"]["login"],
                                                           conf["1"] ["pass"],
                                                           idFrom,
                                                           conf["1"]["keyID"],
                                                           platformaCommission)
        if isNodeCommission and isPlatformCommission:
            return True
        else:
            return False                
        
    def test_activated_contract(self):
        if funcs.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == False:
            self.activateContract()
        walletId = funcs.get_activated_wallet(conf["2"]["url"],
                                              "CostContract", self.token)
        sumsBefore = utils.getUserTokenAmounts(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = utils.get_uid(conf["2"]["url"])
        signature, pubRunner = utils.sign(uid, conf["2"]["url"], keys["key2"])
        balanceRunnerB = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
        dataRunner = utils.login(conf["2"]["url"],keys["key2"])
        tokenRunner = dataRunner ["jwtToken"]
        res = utils.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 1}, tokenRunner)
        result = utils.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                res["hash"], tokenRunner)
        
        node = utils.get_block_gen_node(conf["1"]["dbHost"], conf["1"]["dbName"],
                                        conf["1"]["login"], conf["1"] ["pass"],
                                        result["blockid"])
        sumsAfter = utils.getUserTokenAmounts(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 144530000000000000
        platformaCommission = 4470000000000000
        balanceRunnerA = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
        balanceContractOwnerA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         walletId)
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
        if funcs.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == True:
            self.deactivateContract()
        walletId = funcs.get_activated_wallet(conf["2"]["url"],
                                              "CostContract", self.token)
        sumsBefore = utils.getUserTokenAmounts(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"])
        summBefore = sum(summ[0] for summ in sumsBefore)
        bNodeBalance = self.getNodeBalances()
        tokenRunner, uid = utils.get_uid(conf["2"]["url"])
        signature, pubRunner = utils.sign(uid, conf["2"]["url"], keys["key2"])
        balanceRunnerB = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
        dataRunner = utils.login(conf["2"]["url"],keys["key2"])
        tokenRunner = dataRunner ["jwtToken"]
        res = utils.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 1}, tokenRunner)
        result = utils.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                res["hash"], tokenRunner)
        
        node = utils.get_block_gen_node(conf["1"]["dbHost"], conf["1"]["dbName"],
                                        conf["1"]["login"], conf["1"] ["pass"],
                                        result["blockid"])
        sumsAfter = utils.getUserTokenAmounts(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"])
        summAfter = sum(summ[0] for summ in sumsAfter)
        aNodeBalance = self.getNodeBalances()
        nodeCommission = 144530000000000000
        platformaCommission = 4470000000000000
        commission = nodeCommission + platformaCommission
        balanceRunnerA = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
        balanceContractOwnerA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         walletId)
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
        if funcs.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == False:
            self.activateContract()
        walletId = funcs.get_activated_wallet(conf["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         walletId)
        balanceNodeOwnerB = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     conf["2"]["keyID"])
        commisionWallet = utils.get_commission_wallet(conf["1"]["dbHost"],
                                                      conf["1"]["dbName"],
                                                      conf["1"]["login"],
                                                      conf["1"] ["pass"], 1)
        balanceCommisionB = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     commisionWallet)
        tokenRunner, uid = utils.get_uid(conf["2"]["url"])
        signature, pubRunner = utils.sign(uid, conf["2"]["url"], keys["key2"])
        balanceRunnerB = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
        dataRunner = utils.login(conf["2"]["url"],keys["key2"])
        tokenRunner = dataRunner ["jwtToken"]
        res = utils.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 0}, tokenRunner)
        hash = res["hash"]
        result = utils.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                hash, tokenRunner)
        balanceContractOwnerA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         walletId)
        balanceNodeOwnerA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     conf["2"]["keyID"])
        balanceCommisionA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     commisionWallet)
        balanceRunnerA = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
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
        if funcs.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == True:
            self.deactivateContract()
        walletId = funcs.get_activated_wallet(conf["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         walletId)
        balanceNodeOwnerB = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     conf["2"]["keyID"])
        commisionWallet = utils.get_commission_wallet(conf["1"]["dbHost"],
                                                      conf["1"]["dbName"],
                                                      conf["1"]["login"],
                                                      conf["1"] ["pass"], 1)
        balanceCommisionB = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     commisionWallet)
        commission = utils.get_system_parameter(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     "commission_size")
        tokenRunner, uid = utils.get_uid(conf["2"]["url"])
        signature, pubRunner = utils.sign(uid, conf["2"]["url"], keys["key2"])
        balanceRunnerB = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
        dataRunner = utils.login(conf["2"]["url"],keys["key2"])
        tokenRunner = dataRunner ["jwtToken"]
        res = utils.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 0}, tokenRunner)
        hash = res["hash"]
        result = utils.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                hash, tokenRunner)
        balanceContractOwnerA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         walletId)
        balanceNodeOwnerA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     conf["2"]["keyID"])
        balanceCommisionA = utils.get_balance_from_db(conf["1"]["dbHost"],
                                                     conf["1"]["dbName"],
                                                     conf["1"]["login"],
                                                     conf["1"] ["pass"],
                                                     commisionWallet)
        balanceRunnerA = utils.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                         conf["1"]["dbName"],
                                                         conf["1"]["login"],
                                                         conf["1"] ["pass"],
                                                         pubRunner)
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
        
                
if __name__ == '__main__':
    unittest.main()