import unittest
import requests
import json
import os
import time

from libs import actions
from libs import tools
from libs import db
from libs import api


class TestApi():

    @classmethod
    def setup_class(self):
        global url, token, prKey, pause
        self.config = tools.read_config("nodes")
        url = self.config["2"]["url"]
        pause = tools.read_config("test")["wait_tx_status"]
        prKey = self.config["1"]['private_key']
        self.data = actions.login(url, prKey, 0)
        token = self.data["jwtToken"]
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, result, jwtToken):
        self.unit.assertIn("hash", result)
        hash = result['hash']
        status = actions.tx_status(url, pause, hash, jwtToken)
        if status['blockid'] > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = actions.call_get_api(end, data, token)
        print(result)
        for key in keys:
            self.unit.assertIn(key, result)
        return result

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = actions.call_post_api(end, data, token)
        for key in keys:
            self.unit.assertIn(key, result)
        return result

    def get_error_api(self, endPoint, data):
        end = url + endPoint
        result = actions.call_get_api(end, data, token)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data):
        resp = actions.call_contract(url, prKey, name, data, token)
        resp = self.assert_tx_in_block(resp, token)
        return resp


    # Call from new API func
    def test_ecosystemname(self):
        res = api.ecosystemname(url, token, id=1)
        print(res)

    def test_appparams(self):
        res = api.appparams(url, token, appid=1, names='p1,p2')
        print(res)

    def test_appparam(self):
        res = api.appparam(url, token, appid=1, name='p1')
        print(res)

    def test_ecosystemparams(self):
        res = api.ecosystemparams(url, token, ecosystem=1, names='founder_account,changing_language')
        print(res)

    def test_ecosystemparam(self):
        res = api.ecosystemparam(url, token, name='founder_account', ecosystem=1)
        print(res)

    def test_tables(self):
        res = api.tables(url, token, limit=2, offset=4)
        print(res)

    def test_table(self):
        res = api.table(url, token, name='blocks')
        print(res)

    def test_list(self):
        res = api.list(url, token, name='contracts', limit=2, offset=2, columns='name')
        print(res)

    def test_row(self):
        res = api.row(url, token, tablename='contracts', id=2, columns='name, conditions')
        print(res)

    def test_systemparams(self):
        res = api.systemparams(url, token, names='default_ecosystem_page,default_ecosystem_menu')
        print(res)

    def test_history(self):
        res = api.history(url, token, name='contracts', id=2)
        print(res)
