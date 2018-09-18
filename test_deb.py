import unittest
import requests
import json
import os
import time

import conftest
from libs.actions import Actions
from libs.tools import Tools
from libs.db import Db


class TestDeb():
    '''
    For debug and experiments
    '''

    @classmethod
    def setup_class(self):
        self.createContracts(self)

    def test_example(self):
        print("2")
        print("a_" + Tools.generate_random_name())
        print("b_" + Tools.generate_random_name())
        print(Tools.generate_name_and_code(""))
        #print(self.create_contracts())

    def createContracts(self):
        print("booo")








