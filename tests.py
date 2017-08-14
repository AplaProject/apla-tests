import unittest
import utils
import config
import requests


class GetUidTestCase(unittest.TestCase):
	def test_get_uid(self):
		resp = requests.get(config.config['url'] + '/getuid')
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		uid = int(result['uid'])


class SigntestTestCase(unittest.TestCase):
	def test_signtest_incorrect_private_key(self):
		params = {'forsign': 'smth', 'private': 'incorrect hex'}
		resp = requests.post(config.config['url']+'/signtest/', params=params)
		self.assertEqual(resp.status_code, 400)

	def test_signtest_correct(self):
		resp = requests.post(config.config['url']+'/signtest/', params={'forsign': 'smth', 'private': '123456'})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('signature', result)
		self.assertIn('pubkey', result)


class LoginTestCase(unittest.TestCase):
	def test_login_correct(self):
		cookie, uid = utils.get_uid()
		signature, pubkey = utils.sign(uid)
		resp = requests.post(config.config['url']+'/login', params={'pubkey': pubkey, 'state': 'my_state', 'signature': signature}, headers={'Cookie': cookie})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('address', result)

	def test_login_no_cookie(self):
		_, uid = utils.get_uid()
		signature, pubkey = utils.sign(uid)
		resp = requests.post(config.config['url']+'/login', params={'pubkey': pubkey, 'state': 'my_state', 'signature': signature})
		self.assertEqual(resp.status_code, 400)

	def test_login_no_pubkey(self):
		_, uid = utils.get_uid()
		signature, pubkey = utils.sign(uid)
		resp = requests.post(config.config['url']+'/login', params={'state': 'my_state', 'signature': signature})
		self.assertEqual(resp.status_code, 400)


class BalanceTestCase(unittest.TestCase):
	def setUp(self):
		self.data = utils.login()
	
	def test_balance(self):
		resp = requests.get(config.config['url']+'/balance/' + self.data['address'], headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("amount", result)
		self.assertIn("egs", result)
	

class StateTestCase(unittest.TestCase):
	def setUp(self):
		self.data = utils.login()

	def test_state_list(self):
		resp = requests.get(config.config['url']+'/statelist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertGreaterEqual(int(result['count']), 1)
		self.assertEqual(int(result['count']), len(result['list']))
		item = result['list'][0]
		self.assertIn('name', item)
		self.assertIn('logo', item)
		self.assertIn('id', item)
		self.assertIn('coords', item)

	def test_stateparams_list(self):
		resp = requests.get(config.config['url']+'/stateparamslist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertGreaterEqual(int(result['count']), 1)
		item = result['list'][0]
		self.assertIn('name', item)
		self.assertIn('value', item)
		self.assertIn('conditions', item)
	
	def test_state_param(self):
		resp = requests.get(config.config['url']+'/stateparamslist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertGreaterEqual(int(result['count']), 1)
		item = result['list'][0]
		resp = requests.get(config.config['url']+'/stateparams/' + item['name'], headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('name', result)
		self.assertIn('value', result)
		self.assertIn('conditions', result)


class MenuTestCase(unittest.TestCase):
	def setUp(self):
		self.data = utils.login()

	def get_first_menu_item(self):
		resp = requests.get(config.config['url']+'/menulist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertEqual(int(result['count']), len(result['list']))
		self.assertGreaterEqual(int(result['count']), 1)
		return result['list'][0]

	def test_menu_list(self):
		resp = requests.get(config.config['url']+'/menulist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertEqual(int(result['count']), len(result['list']))
		self.assertGreaterEqual(int(result['count']), 1)
		item = result['list'][0]
		self.assertIn('name', item)

	def test_menu_param(self):
		item = self.get_first_menu_item()
		resp = requests.get(config.config['url']+'/menu/' + item['name'], headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('name', result)
		self.assertIn('value', result)
		self.assertIn('conditions', result)

	def test_change_menu(self):
		item = self.get_first_menu_item()
		data = {'value':'1', 'conditions': 'some_conditions', 'global': '1'}
		sign_res = utils.prepare_tx('PUT', 'menu', item['name'], self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.put(config.config['url']+'/menu/'+item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)

	def test_new_menu(self):
		data = {'value':'1', 'conditions': 'some_conditions', 'global': '1', "name": "mymenu"}
		sign_res = utils.prepare_tx('POST', 'menu', "", self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.post(config.config['url']  + '/menu', data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)

	def test_append_menu(self):
		item = self.get_first_menu_item()
		data = {'value':'new_menu_template', 'global': '0'}
		sign_res = utils.prepare_tx('PUT', 'appendmenu', item['name'], self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.put(config.config['url']  + '/appendmenu/' + item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)


class PageTestCase(unittest.TestCase):
	def setUp(self):
		self.data = utils.login()

	def get_first_page_item(self):
		resp = requests.get(config.config['url']+'/pagelist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertEqual(int(result['count']), len(result['list']))
		self.assertGreaterEqual(int(result['count']), 1)
		item = result['list'][0]
		return item

	def test_page_list(self):
		item = self.get_first_page_item()
		self.assertIn('name', item)
		self.assertIn('menu', item)

	def test_page(self):
		item = self.get_first_page_item()
		resp = requests.get(config.config['url']+'/page/' + item['name'], headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('name', result)
		self.assertIn('menu', result)
		self.assertIn('value', result)
		self.assertIn('conditions', result)

	def test_new_page(self):
		data = {'value':'1', 'conditions': 'some_conditions', 'global': '1', "name": "mypage", "menu": "default_menu"}
		sign_res = utils.prepare_tx('POST', 'page', "", self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.post(config.config['url']  + '/page', data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)
	
	def test_change_page(self):
		item = self.get_first_page_item()
		data = {'value':'1', 'conditions': 'some_conditions', 'global': '1', 'menu': 'default_menu'}
		sign_res = utils.prepare_tx('PUT', 'page', item['name'], self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.put(config.config['url']+'/page/'+item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)
	
	def test_append_page(self):
		item = self.get_first_page_item()
		data = {'value':'new_page_append', 'global': '0'}
		sign_res = utils.prepare_tx('PUT', 'appendpage', item['name'], self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.put(config.config['url']  + '/appendpage/' + item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)


class LangTestCase(unittest.TestCase):
	def setUp(self):
		self.data = utils.login()

	def get_first_lang_item(self):
		resp = requests.get(config.config['url']+'/langlist', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertEqual(int(result['count']), len(result['list']))
		self.assertGreaterEqual(int(result['count']), 1)
		item = result['list'][0]
		return item

	def test_lang_list(self):
		item = self.get_first_lang_item()
		self.assertIn('name', item)
		self.assertIn('trans', item)

	def test_change_lang(self):
		item = self.get_first_lang_item()
		data = {'trans': """{"ru":"trans"}"""}
		sign_res = utils.prepare_tx('PUT', 'lang', item['name'], self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.put(config.config['url']+'/lang/'+item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)

	def test_new_lang(self):
		data = {'name':'mylang',  "trans": "mytrans"}
		sign_res = utils.prepare_tx('POST', 'lang', "", self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.post(config.config['url']  + '/lang', data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn("hash",  result)


class TableTestCase(unittest.TestCase):
	def setUp(self):
		self.data = utils.login()

	def get_first_table_item(self):
		resp = requests.get(config.config['url']+'/tables', headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertEqual(int(result['count']), len(result['list']))
		self.assertGreaterEqual(int(result['count']), 1)
		item = result['list'][0]
		return item

	def test_tables_list(self):
		item = self.get_first_table_item()
		self.assertIn('name', item)

	def test_table(self):
		item = self.get_first_table_item()
		resp = requests.get(config.config['url']+'/table/' + item['name'], headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('name', result)
		self.assertIn('insert', result)
		self.assertIn('new_column', result)
		self.assertIn('general_update', result)
		self.assertIn('columns', result)

	def test_new_table(self):
		data = {'name':'mytable', 'global': '0', "columns": [["mytext", "text", "0"], ["mynum","int64", "1"]]}
		sign_res = utils.prepare_tx('POST', 'table', "", self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.post(config.config['url']+'/table', data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('hash', result)

	def test_change_table(self):
		data = {'insert': 'some_rights', 'new_column': 'some_rights', 'general_update': 'some_rights'}
		item = self.get_first_table_item()
		sign_res = utils.prepare_tx('PUT', 'table', item['name'], self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.put(config.config['url']+'/table/' + item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('hash', result)

	def test_add_column_to_table(self):
		item = self.get_first_table_item()
		data = {'name': 'my_column', 'type': 'int64', 'permissions': 'perm', 'index': '1'}
		sign_res = utils.prepare_tx('POST', 'column/'+item['name'], "", self.data['cookie'], data)
		data.update(sign_res)
		resp = requests.post(config.config['url']+'/column/' + item['name'], data=data, headers={'Cookie': self.data['cookie']})
		self.assertEqual(resp.status_code, 200)
		result = resp.json()
		self.assertIn('hash', result)


if __name__ == '__main__':
	config.read()
	unittest.main()
