import requests
import time
import config
import random
import string
import psycopg2
from collections import Counter

def get_uid(url):
	resp = requests.get(url + '/getuid')
	result = resp.json()
	return result['token'], result['uid']


def sign(forsign, url, prKey):
	resp = requests.post(url + '/signtest/', params={'forsign': forsign, 'private': prKey})
	result = resp.json()
	return result['signature'], result['pubkey']


def login(url, prKey):
	token, uid = get_uid(url)
	signature, pubkey = sign(uid, url, prKey)
	fullToken = 'Bearer ' + token
	resp = requests.post(url +'/login', params={'pubkey': pubkey, 'signature': signature}, headers={'Authorization': fullToken})
	res = resp.json()
	address = res["address"]
	timeToken = res["refresh"]
	jvtToken = 'Bearer ' + res["token"]
	return {"uid": uid, "timeToken": timeToken, "jvtToken": jvtToken, "pubkey": pubkey, "address": address}


def prepare_tx(url, prKey, entity, jvtToken, data):
	urlToCont = url +'/prepare/' + entity
	resp = requests.post(urlToCont, data=data, headers={'Authorization': jvtToken})
	result = resp.json()
	forsign = result['forsign']
	signature, _ = sign(forsign, url, prKey)
	return {"time": result['time'], "signature": signature}

def install(type, log_level, db_host, db_port, db_name, db_user, db_pass, generate_first_block, first_block_dir):
	data = {'type': type, 'log_level': log_level, 'db_host': db_host, 'db_port': db_port, 'db_name': db_name, 'db_user': db_user, 'db_pass': db_pass, 'generate_first_block': generate_first_block, 'first_block_dir': first_block_dir}
	res = requests.post(config.config['url'] + "/install", params=data)
	return res.json()

def call_contract(url, prKey, name, data, jvtToken):
	sign_res = prepare_tx(url,prKey, name, jvtToken, data)
	data.update(sign_res)
	resp = requests.post(url + '/contract/' + name, data=data, headers={"Authorization": jvtToken})
	result = resp.json()
	return result
            
def txstatus(url, sleepTime, hsh, jvtToken):
	time.sleep(sleepTime)
	resp = requests.get(url + '/txstatus/'+ hsh, headers={'Authorization': jvtToken})
	return resp.json()


def generate_random_name():
	name = []
	for _ in range(1, 30):
		sym = random.choice(string.ascii_lowercase)
		name.append(sym)
	return "".join(name)

def compare_keys_cout(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("SELECT key_id FROM block_chain Order by id DESC LIMIT 10")
	keys = cursor.fetchall()
	print(keys)
	firstKey = keys[1]
	secondKey = ""
	for key in keys:
		if key != firstKey:
			secondKey = key
	if secondKey == "":
		return False
	else:	
		keysCounter = Counter(keys)
		firstKeyCount = keysCounter[firstKey]
		secondKeyCount = keysCounter[secondKey]
		compare = firstKeyCount - secondKeyCount
		if(compare > 1)|(compare < -1):
			return False
		else:
			return True 
		
def compare_node_positions(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("SELECT node_position FROM block_chain Order by id DESC LIMIT 10")
	positions = cursor.fetchall()
	print(positions)
	firstKey = positions[1]
	secondKey = ""
	for position in positions:
		i = 0
		while i > 9:
			if position[i] == position[i+1]:
				return False
				break
			else:
				i =+ 2
	return True 

def get_count_records_block_chain(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("SELECT count(*) FROM \"block_chain\"")
	return cursor.fetchall()
		
def get_ten_items(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("SELECT * FROM block_chain Order by id DESC LIMIT 10")
	keys = cursor.fetchall()
	print(keys)
		
def getCountDBObjects(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("select count(*) from INFORMATION_SCHEMA.TABLES WHERE table_schema='public'")
	tables = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_contracts\"")
	contracts = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_pages\"")
	pages = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_menu\"")
	menus = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_blocks\"")
	blocks = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_parameters\"")
	params = cursor.fetchall()
	cursor.execute("SELECT count(*) FROM \"1_languages\"")
	locals = cursor.fetchall()
	return {"tables": tables[0][0], "contracts": contracts[0][0], "pages": pages[0][0], "menus":menus[0][0], "blocks":blocks[0][0], "params": params[0][0], "locals": locals[0][0]}	
