import unittest
from libs import tools, check, actions, contract


class TestCompareNodes(unittest.TestCase):
    config = tools.read_config('nodes')
    unit = unittest.TestCase()

    def test_compare_nodes(self):
        self.unit.assertTrue(check.compare_nodes(
            self.config), 'Error in test_compare_nodes')

    def test_compare_db(self):
        url = self.config[0]['url']
        data = actions.login(url, self.config[0]['private_key'])
        token = data['jwtToken']
        if not check.compare_db(self.config, url, token):
            print('Error in test_compare_db, send one more transaction')
            tx = contract.new_contract(url, self.config[0]['private_key'], token)
            check.is_tx_in_block(url, 30, tx, token)
            unit.assertTrue(check.compare_db(self.config, url, token),
                            'Error in test_compare_db')


if __name__ == '__main__':
    unittest.main()
