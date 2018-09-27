import unittest
import time

from libs import actions, tools

class CompareBlocks(unittest.TestCase):

    def get_load_time(self, url, token, max_block):
        test_conf = tools.read_config("test")
        sec = 1
        while sec < test_conf["wait_upating_node"]:
            max_block_id1 = actions.get_max_block_id(url, token)
            if max_block_id1 == max_block:
                print("Time: ", sec)
                return {"time": sec, "blocks": max_block_id1}
            else:
                sec = sec + 1
        return {"time": test_conf["wait_upating_node"] + 1, "blocks": max_block_id1}
    
    def test_compare_blocks(self):
        node_conf = tools.read_config("nodes")
        test_conf = tools.read_config("test")
        time.sleep(30)
        data2 = actions.login(node_conf[1]['url'], node_conf[0]['private_key'], 0)
        max_block_id2 = actions.get_max_block_id(node_conf[1]["url"], data2["jwtToken"])
        data1 = actions.login(node_conf[0]['url'], node_conf[0]['private_key'], 0)
        res = self.get_load_time(node_conf[0]["url"], data1["jwtToken"], max_block_id2)
        msg = "All " + str(max_block_id2) +\
         " blocks doesn't load in time. Last loaded block is " + str(res['blocks'])
        unit = unittest.TestCase()
        unit.assertLess(res['time'], test_conf["wait_upating_node"], msg)


if __name__ == '__main__':
    unittest.main()