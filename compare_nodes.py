import unittest
from libs import tools, check

class TestCompareNodes():
    config = tools.read_config("nodes")
    unit = unittest.TestCase()

    def test_compare_nodes(self):
        self.unit.assertTrue(check.compare_nodes(self.config), "Error in test_compare_nodes")        

    def test_compare_db(self):
        self.unit.assertTrue(check.compare_db(self.config), "Error in test_compare_db")


if __name__ == '__main__':
    unittest.main()