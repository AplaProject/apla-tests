from random import randint

from locust import HttpLocust, TaskSet, task
from locust.clients import HttpSession

from libs import actions, tools, api
from genesis_blockchain_tools.contract import Contract


class WebsiteTasks(TaskSet):

    def on_start(self):
        print("New locust script")

    @task
    def NewPage(self):
        config = tools.read_config('nodes')
        b = randint(0, len(config))
        url = config[b]['url']
        pr_key = config[b]['private_key']
        data = actions.login(url, pr_key, 0)
        token = data['jwtToken']
        contract_name = 'NewPage'
        name = 'Page_' + tools.generate_random_name()
        data = {'Name': name, 'Value': 'Hello page!', 'ApplicationId': 1,
                'Conditions': 'true', 'Menu': 'default_menu'}
        schema = api.contract(url, token, contract_name)
        contract = Contract(schema=schema, private_key=pr_key,
                            params=data)
        tx_bin_data = contract.concat()
        self.client.post('/sendTx', files={'call1': tx_bin_data},
                         headers={'Authorization': token}, name=contract_name)

class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000