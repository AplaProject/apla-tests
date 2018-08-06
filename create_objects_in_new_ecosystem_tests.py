import unittest
import utils
import config
import requests
import json
import funcs
import os
import time


class CreateObjectsInNewEcosystemTestCase(unittest.TestCase):
    def setUp(self):
        global url, token, prKey, pause
        self.config = config.getNodeConfig()
        url = self.config["2"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = utils.txstatus(url, pause, hash, jwtToken)
        print(status)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
        return result

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_post_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
        return result
            
    def get_error_api(self, endPoint, data):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data, privKey, token):
        resp = utils.call_contract(url, privKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    def test_create_objects_in_new_ecosystem(self):
        # prepare new users keys
        keys = config.getKeys()
        user1_key = keys["key2"]
        user2_key = keys["key4"]

        # login user1 in platform ecosystem
        user1_data = utils.login(url, user1_key, 0, 1)
        user1_token = user1_data["jwtToken"]
        #time.sleep(5)

        # create new ecosystem by user1
        ecosysName = "Ecosys_" + utils.generate_random_name()
        data = {"Name": ecosysName}
        res = self.call("NewEcosystem", data, user1_key, user1_token )
        self.assertGreater(int(res), 0,
                           "BlockId is not generated: " + str(res))
        ecosysNum = funcs.call_get_api(url + "/ecosystems/", "", user1_token)["number"]
        print("ecosysNum = " + str(ecosysNum))

        # login user1 in new ecosystem
        user1_data = utils.login(url, user1_key, 0, ecosysNum)
        user1_token = user1_data["jwtToken"]
        #time.sleep(5)

        # create new contract with conditions = MainCondition
        contract_template = """{
            action {
                $result = "maincond ok"
            }
        }
        """
        code_maincondition, contract_maincondition = utils.generate_name_and_code(contract_template)
        print("contract_maincondition = " + contract_maincondition)
        data = {"Value": code_maincondition, "ApplicationId": 1,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        res = self.call("@1NewContract", data, user1_key, user1_token)
        self.assertGreater(int(res), 0,
                           "BlockId is not generated: " + str(res))

        # create new contract with conditions = true
        contract_template = """{
            action {
                $result = "true ok"
            }
        }
        """
        code_true, contract_true = utils.generate_name_and_code(contract_template)
        print("contract_true = " + contract_true)
        data = {"Value": code_true, "ApplicationId": 1,
                "Conditions": "true"}
        res = self.call("@1NewContract", data, user1_key, user1_token)
        self.assertGreater(int(res), 0,
                           "BlockId is not generated: " + str(res))


        # create pages

        # login user2 in platform ecosystem
        user2_data = utils.login(url, user2_key, 0, 1)
        user2_token = user2_data["jwtToken"]
        user2_keyId = str(user2_data["key_id"])
        user2_pubkey = str(user2_data["pubkey"])
        # time.sleep(5)

        # add user2 in new ecosystem
        contract_add_new_user_template = """{
            action {   
                DBInsert("keys", "id,pub", "%s", "%s")
                }
        }
        """ %(user2_keyId, user2_pubkey)

        code, contract_add_new_user = utils.generate_name_and_code(contract_add_new_user_template)
        print("contract_add_new_user = " + contract_add_new_user)
        data = {"Value": code, "ApplicationId": 1,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        res = self.call("@1NewContract", data, user1_key, user1_token)
        self.assertGreater(int(res), 0,
                           "BlockId is not generated: " + str(res))
        res = self.call(contract_add_new_user, data, user1_key, user1_token)
        self.assertGreater(int(res), 0,
                           "BlockId is not generated: " + str(res))

        # login user2 in new ecosystem
        user2_data = utils.login(url, user2_key, 0, ecosysNum)
        user2_token = user2_data["jwtToken"]
        print(user2_data)

        '''
        print("user1")
        res = self.call(contract_true, data, user2_key, user2_token)
        res = self.call(contract_maincondition, data, user2_key, user2_token)
        '''

        print("user2")
        id = funcs.get_object_id(url, contract_true, "contracts", user2_token)
        print("id = " + str(id))
        code_true = code_true.replace("ok", "new_var")
        print(code_true)
        data = {"Id": id,
                "Value": code_true}
        res = self.call("@1EditContract", data, user2_key, user2_token)
        print(res)

        id = funcs.get_object_id(url, contract_maincondition, "contracts", user2_token)
        print("id = " + str(id))
        code_maincondition = code_maincondition.replace("ok", "new_var")
        print(code_maincondition)
        data = {"Id": id,
                "Value": code_maincondition}
        res = self.call("@1EditContract", data, user2_key, user2_token)
        print(res)





if __name__ == '__main__':
    unittest.main()
