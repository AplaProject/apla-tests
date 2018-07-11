from locust import HttpLocust, TaskSet, task
import utils
import config
import json
import funcs
import requests

class WebsiteTasks(TaskSet):
    def on_start(self):
        global url, token, prKey, pause
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]
    
    @task
    def NewContract(self):
        code, name = utils.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        sign = utils.prepare_tx(url, prKey, "NewContract", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewContract")
        
    @task
    def MoneyTransfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200",
                "Amount": "2"}
        sign = utils.prepare_tx(url, prKey, "MoneyTransfer", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="MoneyTransfer")
     
    @task   
    def NewParameter(self):
        name = "Par_" + utils.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        sign = utils.prepare_tx(url, prKey, "NewParameter", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewParameter")
        
    @task   
    def NewMenu(self):
        name = "Menu_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        sign = utils.prepare_tx(url, prKey, "NewMenu", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewMenu")
        
    @task   
    def NewPage(self):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        sign = utils.prepare_tx(url, prKey, "NewPage", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewPage")
        
    @task   
    def NewBlock(self):
        name = "Block_" + utils.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        sign = utils.prepare_tx(url, prKey, "NewBlock", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
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
        sign = utils.prepare_tx(url, prKey, "NewTable", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewTable")
        
    @task   
    def NewLang(self):
        data = {"AppID": 1, "Name": "Lang_" + utils.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
        sign = utils.prepare_tx(url, prKey, "NewLang", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewLang")
        

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000