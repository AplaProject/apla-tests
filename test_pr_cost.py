import unittest
import config
import funcs
import test_cost
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from model.actions import Actions


class TestPrCost(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global conf, keys, dataCreater
        conf = config.getNodeConfig()
        keys = config.getKeys()
        dataCreater = Actions.login(conf["1"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        contract = config.readFixtures("contracts")
        code = "contract CostContract" + contract["for_cost"]["code"]
        data = {"Wallet": "", "Value": code, "ApplicationId": 1,
                "Conditions": "true"}
        result = Actions.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "NewContract", data, tokenCreater)
        status = Actions.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                  result['hash'], tokenCreater)
        
    def setUp(self):
        self.data = Actions.login(conf["2"]["url"], keys["key2"], 0)
        self.token = self.data["jwtToken"]
        
    def activateContract(self):
        dataCreater = Actions.login(conf["2"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = funcs.get_contract_id(conf["2"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = Actions.call_contract(conf["2"]["url"], conf["1"]["private_key"],
                                     "ActivateContract", data, tokenCreater)
        status = Actions.txstatus(conf["2"]["url"], conf["1"]["time_wait_tx_in_block"],
                                  result['hash'], tokenCreater)
        
    def deactivateContract(self):
        dataCreater = Actions.login(conf["1"]["url"], conf["1"]["private_key"], 0)
        tokenCreater = dataCreater["jwtToken"]
        id = funcs.get_contract_id(conf["1"]["url"], "CostContract", tokenCreater)
        data = {"Id": id}
        result = Actions.call_contract(conf["1"]["url"], conf["1"]["private_key"],
                                     "DeactivateContract", data, tokenCreater)
        status = Actions.txstatus(conf["1"]["url"], conf["1"]["time_wait_tx_in_block"],
                                  result['hash'], tokenCreater)
        
    
        
    def test_activated_contract(self):
        if funcs.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == False:
            test_cost.activateContract()
        walletId = funcs.get_activated_wallet(conf["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            walletId)
        balanceNodeOwnerB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        conf["2"]["keyID"])
        commisionWallet = Actions.get_commission_wallet(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"], 1)
        balanceCommisionB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        commisionWallet)
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Actions.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 1}, tokenRunner)
        hash = res["hash"]
        result = Actions.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  hash, tokenRunner)
        balanceContractOwnerA = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            walletId)
        balanceNodeOwnerA = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        conf["2"]["keyID"])
        balanceCommisionA = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        commisionWallet)
        balanceRunnerA = Actions.get_balance_from_db_by_pub(conf["1"]["dbHost"],
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
        
    def test_activated_contract(self):
        if funcs.is_contract_activated(conf["2"]["url"], "CostContract", self.token) == False:
            self.activateContract()
        walletId = funcs.get_activated_wallet(conf["2"]["url"], "CostContract", self.token)
        balanceContractOwnerB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            walletId)
        balanceNodeOwnerB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        conf["2"]["keyID"])
        commisionWallet = Actions.get_commission_wallet(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"], 1)
        balanceCommisionB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        commisionWallet)
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Actions.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner ["jwtToken"]
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "CostContract", {"State": 1}, tokenRunner)
        hash = res["hash"]
        result = Actions.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  hash, tokenRunner)
        balanceContractOwnerA = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            walletId)
        balanceNodeOwnerA = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        conf["2"]["keyID"])
        balanceCommisionA = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        commisionWallet)
        balanceRunnerA = Actions.get_balance_from_db_by_pub(conf["1"]["dbHost"],
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
        
    def test_money_transfer(self):
        balanceNodeOwnerB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        conf["2"]["keyID"])
        commisionWallet = Actions.get_commission_wallet(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"], 1)
        balanceCommisionB = Actions.get_balance_from_db(conf["1"]["dbHost"],
                                                        conf["1"]["dbName"],
                                                        conf["1"]["login"],
                                                        conf["1"] ["pass"],
                                                        commisionWallet)
        tokenRunner, uid = Actions.get_uid(conf["2"]["url"])
        signature = sign(keys["key2"], uid)
        pubRunner = get_public_key(keys["key2"])
        balanceRunnerB = Actions.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            pubRunner)
        dataRunner = Actions.login(conf["2"]["url"], keys["key2"], 0)
        tokenRunner = dataRunner ["jwtToken"]
        data = {"Recipient": "0005-2070-2000-0006-0200", "Amount": "1000"}
        res = Actions.call_contract(conf["2"]["url"], keys["key2"],
                                  "MoneyTransfer", data, tokenRunner)
        hash = res["hash"]
        result = Actions.txstatus(conf["2"]["url"], conf["2"]["time_wait_tx_in_block"],
                                  hash, tokenRunner)
        balanceRunnerMust = balanceRunnerB - 1000
        balanceRunnerB = Actions.get_balance_from_db_by_pub(conf["1"]["dbHost"],
                                                            conf["1"]["dbName"],
                                                            conf["1"]["login"],
                                                            conf["1"] ["pass"],
                                                            pubRunner)
