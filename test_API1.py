import unittest
import config
import requests
import json
import os
import time
import pytest

from libs.actions import Actions


def jsonToList(json_api_fixture):
    fullList = []
    for key in json_api_fixture:
        for value in range(len(json_api_fixture[key])):
            fullList.append(json_api_fixture[key][value])
    return fullList

def readFixture():
    path = os.path.join(os.getcwd(), "fixtures/api1.json")
    with open(path, 'r') as f:
        data = f.read()
        res = json.loads(data)
    return res

def readFixture1():
    path = os.path.join(os.getcwd(), "fixtures/api2.json")
    with open(path, 'r') as f:
        data = f.read()
        res = json.loads(data)
    return res

input_data_list = jsonToList(readFixture())


tree = readFixture1()['check_get_api']
ecosystems = tree['ecosystems']
ecosystemparams = tree['ecosystemparams']
ecosystemparam = tree['ecosystemparam']


class TestApi():

    def setUp(self):
        global url, token, prKey, pause
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = Actions.login(url, prKey, 0)
        token = self.data["jwtToken"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = Actions.tx_status(url, pause, hash, jwtToken)
        if len(status['blockid']) > 0:
            unittest.TestCase.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = Actions.call_get_api(end, data, token)
        for key in keys:
            print('key = ' + key)
            unittest.TestCase.assertIn(self, key, result)
        return result

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = Actions.call_post_api(end, data, token)
        for key in keys:
            unittest.TestCase.assertIn(self, key, result)
        return result
            
    def get_error_api(self, endPoint, data):
        end = url + endPoint
        result = Actions.call_get_api(end, data, token)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data):
        resp = Actions.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    '''
    @pytest.mark.parametrize("test_input,expected", [
        (i['endPoint'], i['asserts'][0]) for i in input_data_list
    ])
    def test_eval(self, test_input, expected):
        self.setUp()
        res = self.check_get_api(test_input, '', expected)
        print(res)
    '''
    
    # tests ****************************************************
    @pytest.mark.parametrize("test_input,expected", [
        (i['endPoint'],
         i['asserts']) for i in ecosystems
    ])
    def test_ecosystems(self, test_input, expected):
        self.setUp()
        res = self.check_get_api(test_input, '', expected)
        print(res)



    @pytest.mark.parametrize("test_input,expected", [
        (i['endPoint'],
         i['asserts']) for i in ecosystemparams
    ])
    def test_ecosystemparams(self, test_input, expected):
        self.setUp()
        res = self.check_get_api(test_input, '', expected)
        print(res)



    @pytest.mark.parametrize("test_input,expected", [
        (i['endPoint'],
         i['asserts']) for i in ecosystemparam
    ])
    def test_ecosystemparam(self, test_input, expected):
        self.setUp()
        res = self.check_get_api(test_input, '', expected)
        print(res)

