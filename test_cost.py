import unittest
import time
from libs import tools, actions, db, contract, check


NODE_COMISSION = 13968000000000
PLATFORM_COMISSION = 432000000000


class TestCost():
    wait = tools.read_config('test')['wait_tx_status']
    conf = tools.read_config('nodes')
    keys = tools.read_fixtures('keys')

    def setup_class(self):
        self.u = unittest.TestCase()
        TestCost.create_contracts()

    def setup(self):
        self.data = actions.login(self.conf[1]['url'], self.keys['key2'], 0)
        self.token = self.data['jwtToken']

    def get_node_balances(self):
        node_count = len(self.conf)
        i = 0
        node_balance = []
        while i < node_count:
            node_balance.append(actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                          self.conf[i]['keyID']))
            i += 1
        return node_balance

    @staticmethod
    def create_contracts():
        name = 'CostContract'
        data_creater = actions.login(TestCost.conf[0]['url'],
                                     TestCost.conf[0]['private_key'], 0)
        token_creater = data_creater['jwtToken']
        if not actions.is_contract_present(TestCost.conf[0]['url'], token_creater, name):
            cont = tools.read_fixtures('contracts')
            tx = contract.new_contract(TestCost.conf[0]['url'],
                                       TestCost.conf[0]['private_key'],
                                       token_creater, name=name,
                                       source=cont['for_cost']['code'])
            check.is_tx_in_block(
                TestCost.conf[0]['url'], TestCost.wait, tx, token_creater)

    def bind_wallet(self):
        data_wallet = actions.login(self.conf[1]['url'], self.keys['key1'], 0)
        token_creater = data_wallet['jwtToken']
        id = actions.get_contract_id(self.conf[1]['url'], 'CostContract', token_creater)
        tx = contract.bind_wallet(self.conf[1]['url'], self.keys['key1'],
                                  token_creater, id, wallet=data_wallet['address'])
        block = check.is_tx_in_block(self.conf[1]['url'], self.wait, tx, token_creater)
        if block > 0:
            return data_wallet['key_id']
        else:
            print('bind is faild')

    def unbind_wallet(self):
        data_creater = actions.login(
            self.conf[0]['url'], self.conf[0]['private_key'], 0)
        token_creater = data_creater['jwtToken']
        id = actions.get_contract_id(
            self.conf[0]['url'], 'CostContract', token_creater)
        tx = contract.unbind_wallet(self.conf[0]['url'], self.conf[0]['private_key'],
                                    token_creater, id)
        check.is_tx_in_block(self.conf[0]['url'], self.wait, tx, token_creater)

    def is_commissions_in_history(self, node_commision, id_from, platform_commission, node):
        is_node_commission = actions.is_commission_in_history(self.conf[1]['url'], self.token,
                                                              id_from, self.conf[node]['keyID'],
                                                              node_commision)
        is_platform_commission = actions.is_commission_in_history(self.conf[1]['url'], self.token,
                                                                  id_from, self.conf[0]['keyID'],
                                                                  platform_commission)
        if is_node_commission and is_platform_commission:
            return True
        else:
            return False

    def test_bind_wallet(self):
        if not actions.is_contract_activated(self.conf[1]['url'], 'CostContract', self.token):
            bind_wallet = self.bind_wallet()
        time.sleep(10)
        wallet_id = actions.get_activated_wallet(self.conf[1]['url'],
                                                 'CostContract', self.token)
        summ_before = sum(actions.get_user_token_amounts(
            self.conf[1]['url'], self.token))
        b_node_balance = self.get_node_balances()
        data_runner = actions.login(self.conf[1]['url'], self.keys['key2'], 0)
        token_runner = data_runner['jwtToken']
        balance_runner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                 data_runner['key_id'])
        balance_contract_owner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                        wallet_id)
        res = actions.call_contract(self.conf[1]['url'], self.keys['key2'],
                                    'CostContract', {"State": 1}, token_runner)
        result = actions.tx_status(self.conf[1]['url'], self.wait, res, token_runner)
        time.sleep(10)
        
        node = db.get_block_gen_node(self.conf[0]['db'], result['blockid'])
        summ_after = sum(actions.get_user_token_amounts(self.conf[1]['url'], self.token))
        a_node_balance = self.get_node_balances()
        balance_runner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                             wallet_id)
        node_commission = NODE_COMISSION
        platforma_commission = PLATFORM_COMISSION
        in_history = self.is_commissions_in_history(node_commission, wallet_id,
                                                   platforma_commission, node)
        bal_own =  int(balance_contract_owner_b) - (node_commission + platforma_commission)
        if node == 0:
            bal_plat = int(b_node_balance[0]) + node_commission + platforma_commission
            dict_valid = dict(balanceRunner=int(balance_runner_a),
                             platformBalance=int(a_node_balance[0]),
                             balanceOwner=int(balance_contract_owner_a),
                             summ=int(summ_after),
                             history=in_history)
            dict_expect = dict(balanceRunner=int(balance_runner_b),
                               balanceOwner = bal_own,
                              platformBalance=bal_plat,
                              summ=int(summ_before),
                              history=True)
        else:
            dict_valid = dict(balanceRunner=int(balance_runner_a),
                             platformBalance=int(a_node_balance[0]),
                             nodeBalance=int(a_node_balance[node]),
                             balanceOwner=int(balance_contract_owner_a),
                             summ=int(summ_before),
                             history=in_history)
            dict_expect = dict(balanceRunner=int(balance_runner_b),
                               balanceOwner = bal_own,
                              platformBalance=int(b_node_balance[0]) + int(platforma_commission),
                              nodeBalance=int(b_node_balance[node]) + int(node_commission),
                              summ=int(summ_after),
                              history=True)
        self.u.assertDictEqual(dict_valid, dict_expect,
                               'Error in comissions for bind_wallet')

    def test_unbind_wallet(self):
        if actions.is_contract_activated(self.conf[1]['url'], 'CostContract', self.token):
            self.unbind_wallet()
        wallet_id = actions.get_activated_wallet(self.conf[1]['url'],
                                                 'CostContract', self.token)
        summ_before = sum(actions.get_user_token_amounts(
            self.conf[1]['url'], self.token))
        b_node_balance = self.get_node_balances()
        data_runner = actions.login(self.conf[1]['url'], self.keys['key2'], 0)
        token_runner = data_runner['jwtToken']
        balance_runner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        res = actions.call_contract(self.conf[1]['url'], self.keys['key2'],
                                    'CostContract', {'State': 1}, token_runner)
        result = actions.tx_status(
            self.conf[1]['url'], self.wait, res, token_runner)
        time.sleep(10)
        node = db.get_block_gen_node(self.conf[0]['db'], result['blockid'])
        summ_after = sum(actions.get_user_token_amounts(
            self.conf[1]['url'], self.token))
        a_node_balance = self.get_node_balances()
        node_commission = NODE_COMISSION
        platforma_commission = PLATFORM_COMISSION
        commission = node_commission + platforma_commission
        balance_runner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                             wallet_id)
        in_history = self.is_commissions_in_history(node_commission, data_runner['key_id'],
                                                    platforma_commission, node)
        if node == 0:
            dict_valid = {'balanceRunner': int(balance_runner_a),
                          'platformBalance': int(a_node_balance[0]),
                          'summ': int(summ_before),
                          'history': in_history}
            dict_expect = {'balanceRunner': int(balance_runner_b) - int(commission),
                           'platformBalance': int(b_node_balance[0]) + int(commission),
                           'summ': int(summ_after),
                           'history': True}
        else:
            dict_valid = {'balanceRunner': int(balance_runner_a),
                          'platformBalance': int(a_node_balance[0]),
                          'nodeBalance': int(a_node_balance[node]), 'summ': int(summ_before),
                          'history': in_history}
            dict_expect = {'balanceRunner': int(balance_runner_b) - int(commission),
                           'platformBalance': int(b_node_balance[0]) + int(platforma_commission),
                           'nodeBalance': int(b_node_balance[node]) + int(node_commission),
                           'summ': int(summ_after), 'history': True}
        self.u.assertDictEqual(dict_valid, dict_expect,
                               'Error in comissions for unbind_wallet')

    def test_bind_wallet_with_err(self):
        if not actions.is_contract_activated(self.conf[1]['url'], 'CostContract', self.token):
            self.bind_wallet()
        wallet_id = actions.get_activated_wallet(self.conf[1]['url'], 'CostContract',
                                                 self.token)
        balance_contract_owner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                             wallet_id)
        balance_node_owner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                         self.conf[1]['keyID'])
        commision_wallet = actions.get_sysparams_value(self.conf[1]['url'], self.token,
                                                       'commission_wallet')
        balance_commision_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                        commision_wallet)
        data_runner = actions.login(self.conf[1]['url'], self.keys['key2'], 0)
        token_runner = data_runner['jwtToken']
        balance_runner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        res = actions.call_contract(self.conf[1]['url'], self.keys['key2'],
                                    'CostContract', {'State': 0}, token_runner)
        result = actions.tx_status(
            self.conf[1]['url'], self.wait, res, token_runner)
        time.sleep(10)
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                             wallet_id)
        balance_node_owner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                         self.conf[1]['keyID'])
        balance_commision_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                        commision_wallet)
        balance_runner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        dict_valid = dict(balanceContractOwner=balance_contract_owner_a,
                          balanceNodeOwner=balance_node_owner_a,
                          balanceCommision=balance_commision_a,
                          balanceRunner=balance_runner_a)
        dict_expect = dict(balanceContractOwner=balance_contract_owner_b,
                           balanceNodeOwner=balance_node_owner_b,
                           balanceCommision=balance_commision_b,
                           balanceRunner=balance_runner_b)
        self.u.assertDictEqual(dict_valid, dict_expect,
                               'Error in test_bind_wallet_with_err')

    def test_deactive_contract_with_err(self):
        if actions.is_contract_activated(self.conf[1]['url'], 'CostContract', self.token):
            self.deactivate_contract()
        wallet_id = actions.get_activated_wallet(
            self.conf[1]['url'], 'CostContract', self.token)
        balance_contract_owner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                             wallet_id)
        balance_node_owner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                         self.conf[1]['keyID'])
        commision_wallet = actions.get_sysparams_value(
            self.conf[1]['url'], self.token, 'commission_wallet')
        balance_commision_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                        commision_wallet)
        data_runner = actions.login(self.conf[1]['url'], self.keys['key2'], 0)
        token_runner = data_runner['jwtToken']
        balance_runner_b = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        res = actions.call_contract(self.conf[1]['url'], self.keys['key2'],
                                    'CostContract', {'State': 0}, token_runner)
        time.sleep(10)
        result = actions.tx_status(
            self.conf[1]['url'], self.wait, res, token_runner)
        balance_contract_owner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                             wallet_id)
        balance_node_owner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                         self.conf[1]['keyID'])
        balance_commision_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                        commision_wallet)
        balance_runner_a = actions.get_balance_by_id(self.conf[1]['url'], self.token,
                                                     data_runner['key_id'])
        dict_valid = dict(balanceContractOwner=balance_contract_owner_a,
                          balanceNodeOwner=balance_node_owner_a,
                          balanceCommision=balance_commision_a,
                          balanceRunner=balance_runner_a)
        dict_expect = dict(balanceContractOwner=balance_contract_owner_b,
                           balanceNodeOwner=balance_node_owner_b,
                           balanceCommision=balance_commision_b,
                           balanceRunner=balance_runner_b)
        msg = 'balance_contract_owner_a:' + str(balance_contract_owner_a) + '\n' +\
            'balanceContractOwnerE:' + str(balance_contract_owner_b) + '\n' +\
            'balance_node_owner_a:' + str(balance_node_owner_a) + '\n' +\
            'balanceNodeOwnerE:' + str(balance_node_owner_b) + '\n' +\
            'balance_commision_a:' + str(balance_commision_a) + '\n' +\
            'balanceCommisionE:' + str(balance_commision_b) + '\n' +\
            'balance_runner_a:' + str(balance_runner_a) + '\n' +\
            'balanceRunnerE:' + str(balance_runner_b) + '\n'
        self.u.assertDictEqual(dict_valid, dict_expect, msg)
