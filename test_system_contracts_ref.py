import unittest
import config
import requests
import json
import os
import time

from libs.actions import Actions
from libs.tools import Tools
from libs.db import Db



class TestSystemContractsRef(unittest.TestCase):

    @classmethod
    def setup_class(self, cls):
        global url, token, prKey, pause, dbHost, dbName, login, pas
        self.config = config.getNodeConfig()
        url = self.config["1"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
        self.data = Actions.login(url, prKey, 0)
        token = self.data["jwtToken"]

    def test_example(self):
        print(url)

