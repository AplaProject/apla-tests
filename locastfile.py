from locust import HttpLocust, TaskSet, task
import utils
import config
import json
import funcs
import requests
from genesis_blockchain_tools.contract import Contract

class WebsiteTasks(TaskSet):
    def on_start(self):
        global url, token, prKey, pause, ldata
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]
        keys = config.getKeys()
        ldata = utils.login(self.config["2"]["url"],keys["key2"], 0)

    
    @task
    def NewContract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        schema = utils.get_schema(url, "NewContract", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewContract")
        
    @task
    def MoneyTransfer(self):
        data = {"Recipient_Account": ldata['address'],
                "Amount": "1000"}        
        schema = utils.get_schema(url, "TokensSend", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="MoneyTransfer")

     
    @task   
    def NewParameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}        
        schema = utils.get_schema(url, "NewParameter", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewParameter")
        
    @task   
    def NewMenu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1",
                "Conditions": "true"}
        schema = utils.get_schema(url, "NewMenu", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewMenu")
        
    @task   
    def NewPage(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        schema = utils.get_schema(url, "NewPage", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewPage")
        
    @task   
    def NewBlock(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        schema = utils.get_schema(url, "NewBlock", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewBlock")
        
    @task   
    def NewTable(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + utils.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        schema = utils.get_schema(url, "NewTable", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewTable")
        
    @task   
    def NewLang(self):
        data = {"Name": "Lang_" + utils.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        schema = utils.get_schema(url, "NewLang", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewLang")
        

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000