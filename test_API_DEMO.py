import unittest
import json

from libs import actions, tools, api


class TestApi():

    @classmethod
    def setup_class(self):
        global url, token, prKey, pause
        self.config = tools.read_config("nodes")
        url = self.config["2"]["url"]
        pause = tools.read_config("test")["wait_tx_status"]
        prKey = self.config["1"]['private_key']
        self.data = actions.login(url, prKey, 0)
        token = self.data["jwtToken"]
        self.unit = unittest.TestCase()

    def assert_tx_in_block(self, result, jwtToken):
        self.unit.assertIn("hash", result)
        hash = result['hash']
        status = actions.tx_status(url, pause, hash, jwtToken)
        if status['blockid'] > 0:
            self.unit.assertNotIn(json.dumps(status), 'errmsg')
            return status["blockid"]
        else:
            return status["errmsg"]["error"]

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = actions.call_get_api(end, data, token)
        print(result)
        for key in keys:
            self.unit.assertIn(key, result)
        return result

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = actions.call_post_api(end, data, token)
        for key in keys:
            self.unit.assertIn(key, result)
        return result

    def get_error_api(self, endPoint, data):
        end = url + endPoint
        result = actions.call_get_api(end, data, token)
        error = result["error"]
        message = result["msg"]
        return error, message

    def call(self, name, data):
        resp = actions.call_contract(url, prKey, name, data, token)
        resp = self.assert_tx_in_block(resp, token)
        return resp


    # Call from new API func
    def test_getuid(self):
        token, uid = api.getuid(url)
        print(token)
        print(uid)

    def test_login(self):
        private_key = '72c1e198c990f790747e0aa19807a234c7f4417fa4118e621e0e018dbabf0306'
        res = api.login(url, private_key, role_id=0)
        print(res)

    def test_refresh(self):
        private_key = '72c1e198c990f790747e0aa19807a234c7f4417fa4118e621e0e018dbabf0306'
        res_login = api.login(url, private_key, role_id=1)
        res = api.refresh(url, res_login['timeToken'])
        print(res)

    def test_ecosystemname(self):
        res = api.ecosystemname(url, token, id=1)
        print(res)

    def test_appparams(self):
        res = api.appparams(url, token, appid=1, names='p1,p2')
        print(res)

    def test_appparam(self):
        res = api.appparam(url, token, appid=1, name='p1')
        print(res)

    def test_ecosystemparams(self):
        res = api.ecosystemparams(url, token, ecosystem=1, names='founder_account,changing_language')
        print(res)

    def test_ecosystemparam(self):
        res = api.ecosystemparam(url, token, name='founder_account', ecosystem=1)
        print(res)

    def test_tables(self):
        res = api.tables(url, token, limit=2, offset=4)
        print(res)

    def test_table(self):
        res = api.table(url, token, name='blocks')
        print(res)

    def test_list(self):
        res = api.list(url, token, name='contracts', limit=2, offset=2, columns='name')
        print(res)

    def test_row(self):
        res = api.row(url, token, tablename='contracts', id=2, columns='name, conditions')
        print(res)

    def test_systemparams(self):
        res = api.systemparams(url, token, names='default_ecosystem_page,default_ecosystem_menu')
        print(res)

    def test_history(self):
        res = api.history(url, token, name='contracts', id=2)
        print(res)

    def test_interface(self):
        res = api.interface(url, token, entity='page', name='default_page')
        print(res)
        res = api.interface(url, token, entity='menu', name='default')
        print(res)
        res = api.interface(url, token, entity='block', name='block1')
        print(res)
        print(api.interface.__doc__)

    def test_contracts(self):
        res = api.contracts(url, token, limit=2, offset=2)
        print(res)

    def test_contract(self):
        res = api.contract(url, token, name='MainCondition')
        print(res)

    def test_content(self):
        res = api.content(url, token, entity='page', name='default_page')
        print(res)
        res = api.content(url, token, entity='menu', name='default')
        print(res)
        print(api.content.__doc__)

    def test_content_source(self):
        res = api.content_source(url, token, name='default_page')
        print(res)

    def test_content_hash(self):
        res = api.content_hash(url, token, name='default_page')
        print(res)

    def test_content_template(self):
        templ = 'SetVar(mytest, 100) Div(Body: #mytest#)'
        res = api.content_template(url, token, template=templ, source=1)
        print(res)
        res = api.content_template(url, token, template=templ, source=0)
        print(res)

    def test_maxblockid(self):
        res = api.maxblockid(url, token)
        print(res)

    def test_block(self):
        res = api.block(url, token, 1)
        print(res)
        res = api.block(url, token, 5)
        print(res)

    def test_avatar(self):
        res = api.avatar(url, token, 1)
        print(res)
        for el in res.headers:
            print('{}  -  {}'.format(el, res.headers[el]))
        for el in res:
            print(el)

    def test_config_centrifugo(self):
        res = api.config_centrifugo(url, token)
        print(res)