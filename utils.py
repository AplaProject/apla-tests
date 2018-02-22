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
	data = {'forsign': forsign, 'private': prKey}
	resp = requests.post(url + "/signtest/", params=data)
	result = resp.json()
	return result['signature'], result['pubkey']


def login(url, prKey):
	token, uid = get_uid(url)
	signature, pubkey = sign(uid, url, prKey)
	fullToken = 'Bearer ' + token
	data = {'pubkey': pubkey, 'signature': signature}
	head = {'Authorization': fullToken}
	resp = requests.post(url + '/login', params=data, headers=head)
	res = resp.json()
	result = {}
	result["uid"] = uid
	result["timeToken"] = res["refresh"]
	result["jwtToken"] = 'Bearer ' + res["token"]
	result["pubkey"] = pubkey
	result["address"] = res["address"]
	return result


def prepare_tx(url, prKey, entity, jvtToken, data):
	urlToCont = url + '/prepare/' + entity
	heads = {'Authorization': jvtToken}
	resp = requests.post(urlToCont, data=data, headers=heads)
	result = resp.json()
	forsign = result['forsign']
	signature, _ = sign(forsign, url, prKey)
	return {"time": result['time'], "signature": signature}


def call_contract(url, prKey, name, data, jvtToken):
	sign_res = prepare_tx(url, prKey, name, jvtToken, data)
	data.update(sign_res)
	urlEnd = url + '/contract/' + name
	resp = requests.post(urlEnd, data=data, headers={"Authorization": jvtToken})
	result = resp.json()
	return result


def txstatus(url, sleepTime, hsh, jvtToken):
	time.sleep(sleepTime)
	urlEnd = url + '/txstatus/' + hsh
	resp = requests.get(urlEnd, headers={'Authorization': jvtToken})
	return resp.json()


def generate_random_name():
	name = []
	for _ in range(1, 30):
		sym = random.choice(string.ascii_lowercase)
		name.append(sym)
	return "".join(name)


def generate_name_and_code(sourceCode):
	name = "Cont_" + generate_random_name()
	if sourceCode == "":
		sCode = """{data { }	conditions {	}	action {	}	}"""
	else:
		sCode = sourceCode
	code = "contract " + name + sCode
	return code, name


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
		if(compare > 1) | (compare < -1):
			return False
		else:
			return True


def compare_node_positions(dbHost, dbName, login, password, maxBlockId):
	minBlock = maxBlockId - 11
	request = "SELECT node_position FROM block_chain WHERE id>" + str(minBlock) + " AND id<" + str(maxBlockId)
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute(request)
	positions = cursor.fetchall()
	i = 0
	while i < 9:
		if positions[i][0] == positions[i+1][0]:
			return False
			print(positions)
			break
		else:
			i = i + 2
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
	result = {}
	result["tables"] = tables[0][0]
	result["contracts"] = contracts[0][0]
	result["pages"] = pages[0][0]
	result["menus"] = menus[0][0]
	result["blocks"] = blocks[0][0]
	result["params"] = params[0][0]
	result["locals"] = locals[0][0]
	return result


def getUserTokenAmounts(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("select amount from \"1_keys\"")
	amounts = cursor.fetchall()
	return amounts

def get_blockchain_hash(dbHost, dbName, login, password, maxBlockId):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(maxBlockId) + " ORDER BY id) AS t"
	cursor.execute(request)
	hash = cursor.fetchall()
	return hash
