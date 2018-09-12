import os
import json

from libs.actions import Actions


class Tools(object):


    def readExample(self):
        path = os.path.join(os.getcwd(), "fixtures", "example.json")
        with open(path, 'r', encoding='UTF-8') as f:
            data = f.read()
        return json.loads(data)
    
    def jsonToList(self, js):
        fullList = []
        list = []
        tup = ()
        for i in js:
            for element in i:
                list.append(i[element])
            tup = tuple(list)
            fullList.append(tup)
        return fullList
    
    def generate_random_name(self):
        name = []
        for _ in range(1, 30):
            sym = random.choice(string.ascii_lowercase)
            name.append(sym)
        return "".join(name)

    def generate_name_and_code(self, sourceCode):
        name = "Cont_" + self.generate_random_name()
        code = self.generate_code(sourceCode)
        return code, name

    def generate_code(self, contractName, sourceCode):
        if sourceCode == "":
            sCode = """{data { }    conditions {    }    action {    }    }"""
        else:
            sCode = sourceCode
        code = "contract " + contractName + sCode
        return code

