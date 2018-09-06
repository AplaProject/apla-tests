import utils
import config
import requests
import json
import funcs
import os
import time

from model.database_queries import DatabaseQueries
from model.help_actions import HelpActions
from model.simple_test_data import SimpleTestData
from model.actions import Actions


class Application(object):

    def __init__(self):
        global url, token, prKey, pause, dbHost, dbName, login, pas
        self.config = config.getNodeConfig()
        url = self.config["1"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]
        self.db_query = DatabaseQueries()
        self.simple_test_data = SimpleTestData()
        self.help_actions = HelpActions()
        self.actions = Actions()

    def create_ecosystem(self, name):
        hac = self.help_actions
        ac = self.actions
        data = {"Name": hac.generate_random_name(name)}
        res = ac.call("NewEcosystem", data)
        return res

    def universal_f_2(self, name, call_name, cond="true"):
        hac = self.help_actions
        ac = self.actions
        data = {"Name": hac.generate_random_name(name), "Conditions": cond}
        res = ac.call(call_name, data)
        return res

    def universal_f_with_2_param(self, ):
        hac = self.help_actions

    def universal_f_4(self):
        hac = self.help_actions

