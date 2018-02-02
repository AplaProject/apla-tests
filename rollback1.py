import unittest
import utils
import config
import json
import time
import os


class Rollback1TestCase(unittest.TestCase):
    
    def create_contract(self, data):
        code,name = utils.generate_name_and_code("")
        dataC = {}
        if data == "":
            dataC["Wallet"] = ''
            dataC["Value"] = code
            dataC["Conditions"] = "ContractConditions(`MainCondition`)"
        else:
            dataC = data
        url = self.conf["url"]
        token = self.login["jwtToken"]
        prKey = self.conf['private_key']
        resp = utils.call_contract(url, prKey, "NewContract", dataC, token)

    def test_rollback1(self):
        self.conf = config.readMainConfig()
        host = self.conf["dbHost"]
        db = self.conf["dbName"]
        login = self.conf["login"]
        pas = self.conf["pass"]
        dbInformation = utils.getCountDBObjects(host, db, login, pas)
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'w') as fconf:
            json.dump(dbInformation, fconf)
        self.login = utils.login(self.conf["url"], self.conf['private_key'])
        self.create_contract("")
        time.sleep(20)
        
        