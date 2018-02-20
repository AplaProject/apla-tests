import unittest
import utils
import config
import requests
import time
import argparse
import sys

class BlockChainTestCase(unittest.TestCase):

    def get_name_and_code(self):
        name = utils.generate_random_name()
        code = """contract %s {
                       conditions {}
                       action {}
                    }""" % (name,)
        return code,name
    
    def generate_code(self, name):
        code = """contract %s {
                       conditions {}
                       action {
                       var test string}
                    }""" % (name,)
        return code

    def create_contract(self):
        code,name = self.get_name_and_code()
        data = {'Wallet': '', 'Value': code, 'Conditions': """ContractConditions(`MainCondition`)"""}
        resp = utils.call_contract("NewContract", data, self.data["jvtToken"])
        return name
    
    def test_block_chain(self):
        db1 = args.dbName1
        db2 = args.dbName2
        login = args.dbUser
        pas = args.dbPassword
        host = args.dbHost

        ts_count = 30
        config.readMainConfig()
        self.data = utils.login()
        i = 1
        while i < ts_count:
            start = time.time()
            contName = self.create_contract()
            i = i + 1
            sleep = int(args.sleep) - (time.time() - start)
            if sleep > 0:
                time.sleep(sleep)

        time.sleep(15)
        self.assertTrue(utils.compare_node_positions(host, db1, login, pas), "Incorrect order of nodes in block_chain2")
        self.assertTrue(utils.compare_node_positions(host, db2, login, pas), "Incorrect order of nodes in block_chain1")
        maxBlockId = min(utils.get_count_records_block_chain(host, db1, login, pas), utils.get_count_records_block_chain(host, db2, login, pas))
        self.assertEqual(utils.get_blockchain_hash(host, db1, login, pas, maxBlockId), utils.get_blockchain_hash(host, db2, login, pas, maxBlockId),"Different hash")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbHost', default='localhost')
    parser.add_argument('-dbPort', default='5432')
    parser.add_argument('-dbUser', default='postgres')
    parser.add_argument('-dbPassword', default='postgres')
    parser.add_argument('-dbName1', default='apla')
    parser.add_argument('-dbName2', default='apla2')
    parser.add_argument('-sleep', default='1')

    args = parser.parse_args()
    del(sys.argv[1:])

    unittest.main()
    
