import requests
import time
import config
import random
import string
import psycopg2
from collections import Counter

def get_uid():
	resp = requests.get(config.config["url"] + '/getuid')
	result = resp.json()
	return result['token'], result['uid']


def sign(forsign):
	resp = requests.post(config.config["url"] + '/signtest/', params={'forsign': forsign, 'private': config.config['private_key']})
	result = resp.json()
	return result['signature'], result['pubkey']


def login():
	token, uid = get_uid()
	signature, pubkey = sign(uid)
	fullToken = 'Bearer ' + token
	resp = requests.post(config.config["url"] +'/login', params={'pubkey': pubkey, 'signature': signature}, headers={'Authorization': fullToken})
	res = resp.json()
	address = res["address"]
	timeToken = res["refresh"]
	jvtToken = 'Bearer ' + res["token"]
	return {"uid": uid, "timeToken": timeToken, "jvtToken": jvtToken, "pubkey": pubkey, "address": address}


def prepare_tx(entity, jvtToken, data):
	urlToCont = config.config["url"] +'/prepare/' + entity
	resp = requests.post(urlToCont, data=data, headers={'Authorization': jvtToken})
	result = resp.json()
	forsign = result['forsign']
	signature, _ = sign(forsign)
	return {"time": result['time'], "signature": signature}

def install(type, log_level, db_host, db_port, db_name, db_user, db_pass, generate_first_block, first_block_dir):
	data = {'type': type, 'log_level': log_level, 'db_host': db_host, 'db_port': db_port, 'db_name': db_name, 'db_user': db_user, 'db_pass': db_pass, 'generate_first_block': generate_first_block, 'first_block_dir': first_block_dir}
	res = requests.post(config.config['url'] + "/install", params=data)
	return res.json()

def call_contract(name, data, jvtToken):
	sign_res = prepare_tx(name, jvtToken, data)
	data.update(sign_res)
	resp = requests.post(config.config["url"] + '/contract/' + name, data=data, headers={"Authorization": jvtToken})
	result = resp.json()
	return result
            
def txstatus(hsh, jvtToken):
	time.sleep(config.config["time_wait_tx_in_block"])
	resp = requests.get(config.config["url"] + '/txstatus/'+ hsh, headers={'Authorization': jvtToken})
	return resp.json()


def generate_random_name():
	name = []
	for _ in range(1, 30):
		sym = random.choice(string.ascii_lowercase)
		name.append(sym)
	return "".join(name)

def compare_keys_cout():
	connect = psycopg2.connect(host=config.config["dbHost"], dbname=config.config["dbName"], user=config.config["login"], password=config.config["pass"])
	cursor = connect.cursor()
	cursor.execute("SELECT key_id FROM block_chain Order by id DESC LIMIT 10")
	keys = cursor.fetchall()
	firstKey = keys[1]
	secondKey = ""
	for key in keys:
		if key != firstKey:
			secondKey = key
	if secondKey == "":
		return False
	else:	
		keysCounter = Counter(records)
		firstKeyCount = keysCounter[firstKey]
		secondKeyCount = keysCounter[secondKey]
		compare = firstKeyCount - secondKeyCount
		if(compare > 1)|(compare < -1):
			return False
		else:
			return True 
		
	

	
	
