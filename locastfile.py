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
        keys = tools.read_fixtures('keys')
        self.ldata = utils.login(self.config["2"]["url"],keys["key2"], 0)
    
    @task
    def NewContract(self):
        code, name = tools.generate_name_and_code("")
        data = {"Value": code, "ApplicationId": 1, "Conditions": "true"}
        schema = actions.get_schema(url, "NewContract", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewContract")
        
    @task
    def MoneyTransfer(self):
        data = {"Recipient_Account": self.ldata['address'],
                "Amount": "1000"}        
        schema = actions.get_schema(url, "TokensSend", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="MoneyTransfer")

     
    @task   
    def NewParameter(self):
        name = "Par_" + tools.generate_random_name()
        data = {"Name": name, "Value": "test", "Conditions": "true"}        
        schema = actions.get_schema(url, "NewParameter", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewParameter")
        
    @task   
    def NewMenu(self):
        name = "Menu_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Item1",
                "Conditions": "true"}
        schema = actions.get_schema(url, "NewMenu", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewMenu")
        
    @task   
    def NewPage(self):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        schema = actions.get_schema(url, "NewPage", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewPage")
        
    @task   
    def NewBlock(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "Value": "Hello page!", "ApplicationId": 1,
                "Conditions": "true"}
        schema = actions.get_schema(url, "NewBlock", token)
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
        data = {"Name": "Tab_" + tools.generate_random_name(),
                "Columns": column, "ApplicationId": 1,
                "Permissions": permission}
        schema = actions.get_schema(url, "NewTable", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewTable")
        
    @task   
    def NewLang(self):
        data = {"Name": "Lang_" + tools.generate_random_name(),
                "Trans": "{\"en\": \"false\", \"ru\" : \"true\"}"}
        schema = actions.get_schema(url, "NewLang", token)
        contract = Contract(schema=schema, private_key=prKey,
                    params=data)
        tx_bin_data = contract.concat()
        self.client.post("/sendTx", files={'call1': tx_bin_data},
                         headers={"Authorization": token}, name="NewLang")
        
        

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000