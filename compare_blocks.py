import unittest
import utils
import config
import funcs

class CompareBlocks(unittest.TestCase):
    
    def get_load_time(self, url, token, maxBlock):
        maxTime = 300
        sec = 1
        while sec < maxTime:
            maxBlockId1 = funcs.get_max_block_id(url, token)
            if maxBlockId1 == maxBlock:
                return {"time": sec, "blocks": maxBlockId1}
            else:
                sec = sec + 1
        return {"time": 301, "blocks": maxBlockId1}
    
    def test_compare_blocks(self):
        conf = config.getNodeConfig()
        data2 = utils.login(conf['2']['url'], conf['1']['private_key'], 0)
        maxBlockId2 = funcs.get_max_block_id(conf["2"]["url"], data2["jwtToken"])
        data1 = utils.login(conf['1']['url'], conf['1']['private_key'], 0)
        time = self.get_load_time(conf["1"]["url"], data1["jwtToken"], maxBlockId2)
        msg = "All " + str(maxBlockId2) +\
         " blocks doesn't load in time. Last loaded block is " + str(time['blocks'])
        self.assertLess(time['time'], 300, msg)
		
if __name__ == "__main__":
    unittest.main()
    