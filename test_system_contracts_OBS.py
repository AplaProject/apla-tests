import unittest
import os
import time
import json

from libs import actions, tools, db, contract, check, api


class TestSystemContracts():
    config = tools.read_config('nodes')
    url = config[0]['url']
    db = config[0]['db']
    wait = tools.read_config('test')['wait_tx_status']
    pr_key = config[0]['private_key']
    data = actions.login(url, pr_key, 0)
    token = data['jwtToken']
    keys = tools.read_fixtures('keys')

    obs_name = 'OBS1'.lower()
    obs_user = 'user1'
    obs_passw = 'pas1'
    obs_port = '9001'

    obs_name2 = 'OBS2'.lower()
    obs_user2 = 'user2'
    obs_passw2 = 'pas2'
    obs_port2 = '9002'


    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()


    # ********************* OBS

    def test_0NewOBS_for_remove_in_status_is_started(self):
        name = self.obs_name2
        user = self.obs_user2
        passw = self.obs_passw2
        port = self.obs_port2
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'OBS {} created'.format(name)
        self.unit.assertEqual(res['result'], msg, 'error')


    def test_1NewOBS(self):
        name = self.obs_name
        user = self.obs_user
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'OBS {} created'.format(name)
        self.unit.assertEqual(res['result'], msg, 'error')


    def test_2NewOBS_exist(self):
        name = self.obs_name
        user = self.obs_user
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"panic","error":"obs \''+ name + '\' already exists"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_3RunOBS_alrady_runned(self):
        name = self.obs_name
        data = {
            'OBSName': name
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'RunOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"panic","error":"OBS \'' + name + '\' is RUNNING"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_4StopOBS(self):
        name = self.obs_name
        data = {
            'OBSName': name,
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'StopOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'OBS {} stopped'.format(name)
        self.unit.assertEqual(res['result'], msg, 'error')


    def test_44ListOBS(self):
        data = {}
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'ListOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'map[{}:RUNNING {} {}:EXITED {}]'.format(self.obs_name2, self.obs_port2,
                                                        self.obs_name, self.obs_port)
        self.unit.assertEqual(res['result'], msg, 'error')


    def test_5StopOBS_alrady_stopped(self):
        name = self.obs_name
        data = {
            'OBSName': name,
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'StopOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"panic","error":"OBS \'' +name + '\' is EXITED"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_6RemoveOBS_exist_stopped(self):
        name = self.obs_name
        data = {
            'OBSName': name,
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'RemoveOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'OBS {} removed'.format(name)
        self.unit.assertEqual(res['result'], msg, 'error')


    def test_7RemoveOBS_not_exist(self):
        name = self.obs_name
        data = {
            'OBSName': name,
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'RemoveOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"panic","error":"OBS \'' + name + '\' is not exists"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_8RemoveOBS_exist_stopped(self):
        name = self.obs_name2
        data = {
            'OBSName': name,
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'RemoveOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'OBS {} removed'.format(name)
        self.unit.assertEqual(res['result'], msg, 'error')


    def test_9ListOBS(self):
        data = {}
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'ListOBS',
                                    data,
                                    self.token)
        res = actions.tx_status(self.url, self.wait, tx, self.token)
        print(res)
        msg = 'map[]'
        self.unit.assertEqual(res['result'], msg, 'error')

    # Negative NewOBS tests

    def test_NewOBS_empty_name(self):
        name = ''
        user = self.obs_user
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"warning","error":"OBSName was not received"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_name_contain_spaces(self):
        name = 'hello world obs'
        user = self.obs_user
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"error","error":"OBSName can not contain spaces"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_name_begin_with_number(self):
        name = '123hello'
        user = self.obs_user
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"panic","error":"the name cannot begit with a number and must contain alphabetical symbols and numbers"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_name_contain_cyrilic_symbol(self):
        name = 'приветhello'
        user = self.obs_user
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"panic","error":"the name cannot begit with a number and must contain alphabetical symbols and numbers"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_empty_user(self):
        name = self.obs_name
        user = ''
        passw = self.obs_passw
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"warning","error":"DBUser was not received"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_empty_password(self):
        name = self.obs_name
        user = self.obs_name
        passw = ''
        port = self.obs_port
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"warning","error":"DBPassword was not received"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_port_is_zero(self):
        name = self.obs_name
        user = self.obs_name
        passw = self.obs_passw
        port = 0
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"warning","error":"OBS API PORT not received"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


    def test_NewOBS_port_is_negative_digit(self):
        name = self.obs_name
        user = self.obs_name
        passw = self.obs_passw
        port = -65236
        data = {
            'OBSName': name,
            'DBUser': user,
            'DBPassword': passw,
            'OBSAPIPort': port
        }
        tx = actions.call_contract(self.url,
                                    self.pr_key,
                                    'NewOBS',
                                    data,
                                    self.token)
        print(tx)
        msg = '{"type":"warning","error":"OBS API PORT not received"}'
        self.unit.assertEqual(tx['msg'], msg, 'error')


