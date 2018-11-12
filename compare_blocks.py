import unittest
import time

from libs import actions, tools

class CompareBlocks(unittest.TestCase):

    
    def test_compare_blocks(self):
        node_conf = tools.read_config("nodes")
        test_conf = tools.read_config("test")
        time.sleep(30)
        data2 = actions.login(node_conf[1]['url'], node_conf[0]['private_key'], 0)
        max_block_id2 = actions.get_max_block_id(node_conf[1]["url"], data2["jwtToken"])
        data1 = actions.login(node_conf[0]['url'], node_conf[0]['private_key'], 0)
        res = actions.get_load_blocks_time(node_conf[0]["url"], data1["jwtToken"],
                                           max_block_id2, test_conf["wait_upating_node"])
        msg = "All " + str(max_block_id2) +\
         " blocks doesn't load in time. Last loaded block is " + str(res['blocks'])
        unit = unittest.TestCase()
        unit.assertLess(res['time'], test_conf["wait_upating_node"], msg)


if __name__ == '__main__':
    unittest.main()