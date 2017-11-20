import requests
import time
import config
import random
import string
import postgresql
import psycopg2
from collections import Counter

def get_uid(url):
	resp = requests.get(url + '/getuid')
	result = resp.json()
	return result['token'], result['uid']


def sign(forsign, url, privateKey):
	resp = requests.post(url + '/signtest/', params={'forsign': forsign, 'private': privateKey})
	result = resp.json()
	return result['signature'], result['pubkey']


def login(url, privateKey):
	token, uid = get_uid(url)
	signature, pubkey = sign(uid, url, privateKey)
	fullToken = 'Bearer ' + token
	resp = requests.post(url +'/login', params={'pubkey': pubkey, 'signature': signature}, headers={'Authorization': fullToken})
	res = resp.json()
	address = res["address"]
	timeToken = res["refresh"]
	jvtToken = 'Bearer ' + res["token"]
	return {"uid": uid, "timeToken": timeToken, "jvtToken": jvtToken, "pubkey": pubkey, "address": address}


def prepare_tx(entity, jvtToken, data, url, privateKey):
	urlToCont = url +'/prepare/' + entity
	resp = requests.post(urlToCont, data=data, headers={'Authorization': jvtToken})
	result = resp.json()
	forsign = result['forsign']
	signature, _ = sign(forsign, url, privateKey)
	return {"time": result['time'], "signature": signature}


def txstatus(hsh, url, jvtToken, wait):
	time.sleep(wait)
	resp = requests.get(url + '/txstatus/'+ hsh, headers={'Authorization': jvtToken})
	return resp.json()


def generate_random_name():
	name = []
	for _ in range(1, 30):
		sym = random.choice(string.ascii_lowercase)
		name.append(sym)
	return "".join(name)

def compare_keys_cout():
	db = postgresql.open('pq://postgres:postgres@localhost:5432/aplafront')
	conf = "host='localhost' dbname='aplahost' user='postgres' password='postgres'"
	connect = psycopg2.connect(host='localhost', dbname='aplafront', user='postgres', password='postgres')
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

	
	
