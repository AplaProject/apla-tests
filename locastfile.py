from locust import HttpLocust, TaskSet, task
from libs import actions
from libs import tools

class WebsiteTasks(TaskSet):
    def on_start(self):
        self.config = tools.read_config("nodes")
        self.url = self.config["2"]["url"]
        self.pause = tools.read_config("test")["wait_tx_status"]
        self.prKey = self.config["1"]['private_key']
        self.data = actions.login(self.url, self.prKey, 0)
        self.token = self.data["jwtToken"]
    
    @task
    def NewContract(self):
        code, name = self.t.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.prKey, "NewContract", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewContract")
        
    @task
    def MoneyTransfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200",
                "Amount": "2"}
        sign = actions.prepare_tx(self.url, self.prKey, "MoneyTransfer", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="MoneyTransfer")
     
    @task   
    def NewParameter(self):
        name = "Par_" + tools.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.prKey, "NewParameter", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewParameter")
        
    @task   
    def NewMenu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.prKey, "NewMenu", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewMenu")
        
    @task   
    def NewPage(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        sign = actions.prepare_tx(self.url, self.prKey, "NewPage", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewPage")
        
    @task   
    def NewBlock(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.prKey, "NewBlock", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewBlock")
        
    @task   
    def NewTable(self):
        column = """[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]"""
        permission = """{"insert": "false",
        "update" : "true","new_column": "true"}"""
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        sign = actions.prepare_tx(self.url, self.prKey, "NewTable", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewTable")
        
    @task   
    def NewLang(self):
        data = {"AppID": 1, "Name": "Lang_" + tools.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
        sign = actions.prepare_tx(self.url, self.prKey, "NewLang", self.token, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], dataContract,
                         headers={"Authorization": self.token}, name="NewLang")
        

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000