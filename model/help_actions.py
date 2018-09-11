import os
import json

from model.actions import Actions


class HelpActions(object):

    def generate_random_name(self, name):
        return name + Actions.generate_random_name()

    def readExample(self):
        path = os.path.join(os.getcwd(), "fixtures", "example.json")
        with open(path, 'r', encoding='UTF-8') as f:
            data = f.read()
        return json.loads(data)
