from locust import HttpLocust, TaskSet, task
from libs import actions, tools, api
from genesis_blockchain_tools.contract import Contract
from genesis_blockchain_tools.crypto import gen_keypair


class WebsiteTasks(TaskSet):
    def on_start(self):
        self.config = tools.read_config('nodes')
        self.url = self.config[0]['url']
        self.pause = tools.read_config('test')['wait_tx_status']
        self.pr_key = self.config[0]['private_key']
        self.data = actions.login(self.url, self.pr_key, 0)
        self.token = self.data['jwtToken']
        keys = tools.read_fixtures('keys')
        self.ldata = actions.login(self.config[1]['url'], keys['key2'], 0)


    @task
    def NewUser(self):
        contract_name = 'NewUser'
        priv_key, pub_key = gen_keypair()
        data = {'NewPubkey': pub_key}
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
