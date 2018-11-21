from random import randint

from locust import HttpLocust, TaskSet, task
from locust.clients import HttpSession

from libs import actions, tools, api
from genesis_blockchain_tools.contract import Contract


class WebsiteTasks(TaskSet):
    def on_start(self):
        config = tools.read_config('nodes')
        self.url = self.parent.host
        self.pr_key = self.config[0]['private_key']
        self.data = actions.login(self.url, self.pr_key, 0)
        self.token = self.data['jwtToken']


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

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000