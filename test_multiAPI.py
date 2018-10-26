import unittest

from libs import actions, tools


class TestMultiApi():
    config = tools.read_config("nodes")
    url = config[1]["url"]
    wait = tools.read_config("test")["wait_tx_status"]
    pr_key = config[0]['private_key']
    data = actions.login(url, pr_key, 0)
    token = data["jwtToken"]

    @classmethod
    def setup_class(self):
        self.unit = unittest.TestCase()

    def assert_multi_tx_in_block(self, result, jwt_token):
        self.unit.assertIn("hashes", result)
        hashes = result['hashes']
        result = actions.tx_status_multi(self.url, self.wait, hashes, jwt_token)
        for status in result.values():
            self.unit.assertNotIn('errmsg', status)
            self.unit.assertGreater(int(status["blockid"]), 0, "BlockID not generated")

    def call_multi(self, name, data):
        resp = actions.call_multi_contract(self.url, self.pr_key, name, data, self.token, False)
        resp = self.assert_multi_tx_in_block(resp, self.token)
        return resp


    def test_new_interface_block(self):
        contract_name = "NewBlock"
        block = "Block_" + tools.generate_random_name()
        data = [{"contract": contract_name,
                 "params":{"Name": block, "Value": "Hello page!", "ApplicationId": "1",
                "Conditions": "true"}}]
        res = self.call_multi(contract_name, data)

    def test_new_interface_block_multi(self):
        contract_name = "NewBlock"
        data = [{"contract": contract_name,
                 "params": {"Name": "Block_" + tools.generate_random_name(), "Value": "Hello page!",
                            "ApplicationId": "1",
                            "Conditions": "true"}} for _ in range(2)]
        res = self.call_multi(contract_name, data)
     
    def test_new_lang(self):
        contract_name = "NewLang"
        name_lang = "Lang_" + tools.generate_random_name()
        data = [{"contract": contract_name,
                 "params": {"Name": name_lang,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\"," +\
                "\"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}}]
        res = self.call_multi(contract_name, data)

    def test_new_page(self):
        contract_name = "NewPage"
        name = "Page_" + tools.generate_random_name()
        data = [{"contract": contract_name,
                 "params":{"Name":name, "Value":"SetVar(a,\"Hello\") \n Div(Body: #a#)", "Conditions":"true", "Menu":"default_menu", "ApplicationId": "1"}}]
        res = self.call_multi(contract_name, data)
