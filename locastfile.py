from locust import HttpLocust, TaskSet, task
from libs import actions, tools

class WebsiteTasks(TaskSet):
    def on_start(self):
        self.config = tools.read_config("nodes")
        self.url = self.config["2"]["url"]
        self.pause = tools.read_config("test")["wait_tx_status"]
        self.pr_key = self.config["1"]['private_key']
        self.data = actions.login(self.url, self.pr_key, 0)
        self.token = self.data["jwtToken"]
    
    @task
    def NewContract(self):
        code, name = self.t.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.pr_key, "NewContract", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="NewContract")
        
    @task
    def MoneyTransfer(self):
        data = {"Recipient": "0005-2070-2000-0006-0200",
                "Amount": "2"}
        sign = actions.prepare_tx(self.url, self.pr_key, "MoneyTransfer", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="MoneyTransfer")
     
    @task   
    def NewParameter(self):
        name = "Par_" + tools.generate_random_name()
        data = {"Name": name, "Value": "test", "ApplicationId": 1,
                "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.pr_key, "NewParameter", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="NewParameter")
        
    @task   
    def NewMenu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1", "ApplicationId": 1,
                "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.pr_key, "NewMenu", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="NewMenu")
        
    @task   
    def NewPage(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        sign = actions.prepare_tx(self.url, self.pr_key, "NewPage", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="NewPage")
        
    @task   
    def NewBlock(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        sign = actions.prepare_tx(self.url, self.pr_key, "NewBlock", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
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
        sign = actions.prepare_tx(self.url, self.pr_key, "NewTable", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="NewTable")
        
    @task   
    def NewLang(self):
        data = {"AppID": 1, "Name": "Lang_" + tools.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}",
                "ApplicationId": 1}
        sign = actions.prepare_tx(self.url, self.pr_key, "NewLang", self.token, data)
        data_contract = {"time": sign['time'], "signature": sign["signature"]}
        self.client.post("/contract/" + sign["reqID"], data_contract,
                         headers={"Authorization": self.token}, name="NewLang")
        

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000