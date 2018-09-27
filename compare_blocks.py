import unittest
import time

from libs import actions, tools

class CompareBlocks(unittest.TestCase):

    def get_load_time(self, url, token, maxBlock):
        testConf = tools.read_config("test")
        sec = 1
        while sec < testConf["wait_upating_node"]:
            maxBlockId1 = actions.get_max_block_id(url, token)
            if maxBlockId1 == maxBlock:
                print("Time: ", sec)
                return {"time": sec, "blocks": maxBlockId1}
            else:
                sec = sec + 1
        return {"time": testConf["wait_upating_node"] + 1, "blocks": maxBlockId1}
    
    def test_compare_blocks(self):
        nodeConf = tools.read_config("nodes")
        testConf = tools.read_config("test")
        time.sleep(30)
        data2 = actions.login(nodeConf[1]['url'], nodeConf[0]['private_key'], 0)
        maxBlockId2 = actions.get_max_block_id(nodeConf[1]["url"], data2["jwtToken"])
        data1 = actions.login(nodeConf[0]['url'], nodeConf[0]['private_key'], 0)
        res = self.get_load_time(nodeConf[0]["url"], data1["jwtToken"], maxBlockId2)
        msg = "All " + str(maxBlockId2) +\
         " blocks doesn't load in time. Last loaded block is " + str(res['blocks'])
        unit = unittest.TestCase()
        unit.assertLess(res['time'], testConf["wait_upating_node"], msg)


if __name__ == '__main__':
    unittest.main()