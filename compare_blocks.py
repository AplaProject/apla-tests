import unittest
import time

from libs.actions import Actions
from libs.tools import Tools

class CompareBlocks(unittest.TestCase):

    def get_load_time(self, url, token, maxBlock):
        testConf = Tools.readConfig("test")
        sec = 1
        while sec < testConf["wait_upating_node"]:
            maxBlockId1 = Actions.get_max_block_id(url, token)
            if maxBlockId1 == maxBlock:
                print("Time: ", sec)
                return {"time": sec, "blocks": maxBlockId1}
            else:
                sec = sec + 1
        return {"time": testConf["wait_upating_node"] + 1, "blocks": maxBlockId1}
    
    def test_compare_blocks(self):
        nodeConf = Tools.readConfig("nodes")
        time.sleep(30)
        data2 = Actions.login(nodeConf['2']['url'], nodeConf['1']['private_key'], 0)
        maxBlockId2 = Actions.get_max_block_id(nodeConf["2"]["url"], data2["jwtToken"])
        data1 = Actions.login(nodeConf['1']['url'], nodeConf['1']['private_key'], 0)
        res = self.get_load_time(conf["1"]["url"], data1["jwtToken"], maxBlockId2)
        msg = "All " + str(maxBlockId2) +\
         " blocks doesn't load in time. Last loaded block is " + str(res['blocks'])
        self.assertLess(res['time'], testConf["wait_upating_node"], msg)


if __name__ == '__main__':
    unittest.main()