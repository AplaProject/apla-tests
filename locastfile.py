from locust import HttpLocust, TaskSet, task
from libs import actions, tools, api
from genesis_blockchain_tools.contract import Contract


class WebsiteTasks(TaskSet):
    def on_start(self):
        self.config = tools.read_config('nodes')
        self.url = self.client.base_url
        self.pause = tools.read_config('test')['wait_tx_status']
        self.pr_key = self.config[0]['private_key']
        self.data = actions.login(self.url, self.pr_key, 0)
        self.token = self.data['jwtToken']
        keys = tools.read_fixtures('keys')
        self.ldata = actions.login(self.config[1]['url'], keys['key2'], 0)
        self.before_time = datetime.datetime.now()
        self.before_trs = api.metrics(self.url, self.token, 'transactions')['count']
        
    def on_stop(self):
        after_time = datetime.datetime.now()
        after_trs = api.metrics(self.url, self.token, 'transactions')['count']
        trs = int(after_trs) - int(self.before_trs)
        dur = after_time - self.before_time
        speed = trs/dur
        data = {"speed": speed}
        print("Speed: ", str(speed), " in second")
        file = os.path.join(os.getcwd(), 'speed.txt')
        with open(file, 'w') as f:
            f.write(data)
    
    @task
    def NewContract(self):
        contract_name = 'NewContract'
        code, name = tools.generate_name_and_code('')
        data = {'Value': code, 'ApplicationId': 1, 'Conditions': 'true'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def TokensSend(self):
        contract_name = 'TokensSend'
        data = {'Recipient': self.ldata['address'],
                'Amount': '1000'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def NewParameter(self):
        contract_name = 'NewParameter'
        name = 'Par_' + tools.generate_random_name()
        data = {'Name': name, 'Value': 'test', 'Conditions': 'true'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def NewMenu(self):
        contract_name = 'NewMenu'
        name = 'Menu_' + tools.generate_random_name()
        data = {'Name': name, 'Value': 'Item1',
                'Conditions': 'true'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def NewPage(self):
        contract_name = 'NewPage'
        name = 'Page_' + tools.generate_random_name()
        data = {'Name': name, 'Value': 'Hello page!', 'ApplicationId': 1,
                'Conditions': 'true', 'Menu': 'default_menu'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def NewBlock(self):
        contract_name = 'NewBlock'
        name = 'Block_' + tools.generate_random_name()
        data = {'Name': name, 'Value': 'Hello page!', 'ApplicationId': 1,
                'Conditions': 'true'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def NewTable(self):
        contract_name = 'NewTable'
        column = '''[{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"}]'''
        permission = '''{"insert": "false",
        "update" : "true","new_column": "true"}'''
        data = {'Name': 'Tab_' + tools.generate_random_name(),
                'Columns': column, 'ApplicationId': 1,
                'Permissions': permission}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)

    @task
    def NewLang(self):
        contract_name = 'NewLang'
        data = {'Name': 'Lang_' + tools.generate_random_name(),
                'Trans': '{"en": "false", "ru" : "true"}'}
        schema = api.contract(self.url, self.token, contract_name)
        contract = Contract(schema=schema, private_key=self.pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': self.token}, name=contract_name)


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000
