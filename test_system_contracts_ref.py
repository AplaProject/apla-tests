import unittest
import utils
import config
import requests
import json
import funcs
import os
import time

from model.database_queries import DatabaseQueries
from model.help_actions import HelpActions
from model.simple_test_data import SimpleTestData


class TestSystemContractsRef(unittest.TestCase):

    def test_create_ecosystem(self, app):
        res = app.create_ecosystem("Ecosys_")
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))

    def test_edit_application(self, app):
        res = app.universal_f_2("App", "NewApplication")
        self.assertGreater(res["blockid"], 0,
                           "BlockId is not generated: " + str(res))
        #!!!

    def test_edit_ecosystem_name(self, app):
        pass

