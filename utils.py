import requests
import time
import config
import random
import string

def get_uid():
	resp = requests.get(config.config['url'] + '/getuid')
	cookie = resp.headers['Set-Cookie'].split(';')[0]
	result = resp.json()
	return cookie, result['uid']


def sign(forsign):
	resp = requests.post(config.config['url']+'/signtest/', params={'forsign': forsign, 'private': config.config['private_key']})
	result = resp.json()
	return result['signature'], result['pubkey']


def login():
	cookie, uid = get_uid()
	signature, pubkey = sign(uid)
	resp = requests.post(config.config['url']+'/login', params={'pubkey': pubkey, 'state': config.config['state'], 'signature': signature}, headers={'Cookie': cookie})
	address = resp.json()["address"]
	return {"cookie": cookie, "uid": uid, "signature": signature, "pubkey": pubkey, "address": address}


def prepare_tx(method, entity, entity_name, cookie, data):
	url = config.config['url']+'/prepare/' + entity
	if entity_name != "":
		url += '/' + entity_name
	if method == 'PUT':
		resp = requests.put(url, 
				data=data,
				headers={'Cookie': cookie})
	elif method == 'POST':
		resp = requests.post(url, 
				data=data,
				headers={'Cookie': cookie})
	result = resp.json()
	forsign = result['forsign']
	signature, _ = sign(forsign)
	return {"time": result['time'], "signature": signature}


def txstatus(hsh, cookie):
	time.sleep(config.config['time_wait_tx_in_block'])
	resp = requests.get(config.config['url'] + '/txstatus/'+ hsh, headers={"Cookie": cookie})
	return resp.json()


def generate_random_name():
	name = []
	for _ in range(1, 30):
		sym = random.choice(string.ascii_lowercase)
		name.append(sym)
	return "".join(name)
