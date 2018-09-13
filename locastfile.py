from locust import HttpLocust, TaskSet, task
import config
from libs.actions import Actions
from libs.tools import Tools

class WebsiteTasks(TaskSet):
    def on_start(self):
        global url, token, prKey, pause
        self.config = Tools.readConfig("nodes")
        url = self.config["2"]["url"]
        pause = Tools.readConfig("test")["wait_tx_status"]
        prKey = self.config["1"]['private_key']
        self.data = Actions.login(url, prKey, 0)
        token = self.data["jwtToken"]
    
    @task
    def NewContract(self):
        code, name = Tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        sign = Actions.prepare_tx(url, prKey, "NewContract", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewContract")
        
    @task
    def MoneyTransfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200",
                "Amount": "2"}
        sign = Actions.prepare_tx(url, prKey, "MoneyTransfer", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="MoneyTransfer")
     
    @task   
    def NewParameter(self):
        name = "Par_" + Tools.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        sign = Actions.prepare_tx(url, prKey, "NewParameter", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewParameter")
        
    @task   
    def NewMenu(self):
        name = "Menu_" + Tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        sign = Actions.prepare_tx(url, prKey, "NewMenu", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewMenu")
        
    @task   
    def NewPage(self):
        name = "Page_" + Tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        sign = Actions.prepare_tx(url, prKey, "NewPage", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewPage")
        
    @task   
    def NewBlock(self):
        name = "Block_" + Tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        sign = Actions.prepare_tx(url, prKey, "NewBlock", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewBlock")
        
    @task   
    def NewTable(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + Tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        sign = Actions.prepare_tx(url, prKey, "NewTable", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewTable")
        
    @task   
    def NewLang(self):
        data = {"AppID": 1, "Name": "Lang_" + Tools.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
        sign = Actions.prepare_tx(url, prKey, "NewLang", token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": token}, name="NewLang")
        

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000