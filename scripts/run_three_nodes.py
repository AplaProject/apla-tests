import subprocess
import time
import os
import json
import shutil


def test_three_nodes(request):


	curDir = os.path.dirname(os.path.abspath(__file__))

	binary = os.path.abspath(request.config.getoption('--binary'))
	work_dir = os.path.abspath(request.config.getoption('--workDir'))
	work_dir1 = os.path.join(work_dir, 'node1')
	work_dir2 = os.path.join(work_dir, 'node2')
	work_dir3 = os.path.join(work_dir, 'node3')
	first_block_path = os.path.join(work_dir, '1block')


	if os.path.exists(work_dir):
		shutil.rmtree(work_dir)
	os.makedirs(work_dir1)
	os.makedirs(work_dir2)
	os.makedirs(work_dir3)

	# Create config for centrifugo
	cen_config = os.path.join(request.config.getoption('--centrifugo'), "config.json")
	lines_c = []
	lines_c.insert(0, "{\n")
	lines_c.insert(1, "\"secret\": \"4597e75c-4376-42a6-8c1f-7e3fc7eb2114\",\n")
	lines_c.insert(2, "\"admin_secret\": \"admin\"\n")
	lines_c.insert(3, "}")
	with open(cen_config, 'w') as fconf:
		fconf.write(''.join(lines_c))

	# Run centrifugo
	cen_path = os.path.join(request.config.getoption('--centrifugo'), "centrifugo")
	centrifugo = subprocess.Popen([
		cen_path,
		'--config=config.json',
		'--admin',
		'--insecure_admin',
		'--web'
	])
	time.sleep(3)

	# Generate config for first node
	config1 = subprocess.Popen([
		binary,
		'config',
		'--dataDir='+work_dir1,
		'--firstBlock='+first_block_path,
		'--dbPassword='+request.config.getoption('--dbPassword'),
		'--centUrl=http://127.0.0.1:8000',
		'--centSecret=4597e75c-4376-42a6-8c1f-7e3fc7eb2114',
		'--dbName='+request.config.getoption('--dbName1')
	])
	time.sleep(3)

	#Generate keys for first block
	keys1 = subprocess.Popen([
		binary,
		'generateKeys',
		'--config='+work_dir1+'/config.toml'
	])
	time.sleep(3)

	#Generate first block
	firstBlock = subprocess.Popen([
		binary,
		'generateFirstBlock',
		'--config='+work_dir1+'/config.toml'
	])
	time.sleep(3)

	#Init data base
	firstBlock = subprocess.Popen([
		binary,
		'initDatabase',
		'--config='+work_dir1+'/config.toml'
	])
	time.sleep(3)

	#Start first node
	startFirstNode = subprocess.Popen([
		binary,
		'start',
		'--config='+work_dir1+'/config.toml'
	])
	time.sleep(3)

	#Generate config for second node
	generateConfig2 = subprocess.Popen([
		binary,
		'config',
		'--dataDir='+work_dir2,
		'--firstBlock='+first_block_path,
		'--dbName='+request.config.getoption('--dbName2'),
		'--tcpPort='+request.config.getoption('--tcpPort2'),
		'--httpPort='+request.config.getoption('--httpPort2'),
		'--firstBlock='+first_block_path,
		'--dbPassword='+request.config.getoption('--dbPassword'),
		'--centUrl="http://127.0.0.1:8000"',
		'--centSecret="4597e75c-4376-42a6-8c1f-7e3fc7eb2114"',
		'--nodesAddr='+"127.0.0.1:"+request.config.getoption('--tcpPort1')
	])
	time.sleep(3)

	#Generate keys for second node
	generateKeys = subprocess.Popen([
		binary,
		'generateKeys',
		'--config='+work_dir2+'/config.toml'
	])
	time.sleep(3)

	#Generate config for third node
	generateConfig3 = subprocess.Popen([
		binary,
		'config',
		'--dataDir='+work_dir3,
		'--firstBlock='+first_block_path,
		'--dbName=' + request.config.getoption('--dbName3'),
		'--tcpPort='+request.config.getoption('--tcpPort3'),
		'--httpPort='+request.config.getoption('--httpPort3'),
		'--firstBlock='+first_block_path,
		'--dbPassword='+request.config.getoption('--dbPassword'),
		'--centUrl="http://127.0.0.1:8000"',
		'--centSecret="4597e75c-4376-42a6-8c1f-7e3fc7eb2114"',
		'--nodesAddr='+"127.0.0.1:"+request.config.getoption('--tcpPort1')
	])
	time.sleep(3)

	#Generate keys for third node
	generateKeys = subprocess.Popen([
		binary,
		'generateKeys',
		'--config='+work_dir3+'/config.toml'
	])
	time.sleep(3)

	#Init database
	startFirstNode = subprocess.Popen([
		binary,
		'initDatabase',
		'--config='+work_dir2+'/config.toml'
	])
	time.sleep(3)

	#Start third node
	startFirstNode = subprocess.Popen([
		binary,
		'start',
		'--config='+work_dir2+'/config.toml'
	])
	time.sleep(3)

	#Init database
	startThirdNode = subprocess.Popen([
		binary,
		'initDatabase',
		'--config='+work_dir3+'/config.toml'
	])
	time.sleep(3)

	#Start third node
	startThirdNode = subprocess.Popen([
		binary,
		'start',
		'--config='+work_dir3+'/config.toml'
	])
	time.sleep(3)

	with open(os.path.join(work_dir1, 'PrivateKey'), 'r') as f:
		priv_key1 = f.read()
	with open(os.path.join(work_dir1, 'PublicKey'), 'r') as f:
		pub_key1 = f.read()
	with open(os.path.join(work_dir2, 'PrivateKey'), 'r') as f:
		priv_key2 = f.read()
	with open(os.path.join(work_dir3, 'PrivateKey'), 'r') as f:
		priv_key3 = f.read()
	with open(os.path.join(work_dir1, 'KeyID'), 'r') as f:
		key_id1 = f.read()
	with open(os.path.join(work_dir1, 'NodePublicKey'), 'r') as f:
		node_pub_key1 = f.read()
	with open(os.path.join(work_dir2, 'KeyID'), 'r') as f:
		key_id2 = f.read()
	with open(os.path.join(work_dir2, 'NodePublicKey'), 'r') as f:
		node_pub_key2 = f.read()
	with open(os.path.join(work_dir2, 'PublicKey'), 'r') as f:
		pub_key2 = f.read()
	with open(os.path.join(work_dir3, 'KeyID'), 'r') as f:
		key_id3 = f.read()
	with open(os.path.join(work_dir3, 'NodePublicKey'), 'r') as f:
		node_pub_key3 = f.read()
	with open(os.path.join(work_dir3, 'PublicKey'), 'r') as f:
		pub_key3 = f.read()

	#-------------------------



	config = [
		{
			"url": "http://localhost:" + request.config.getoption('--httpPort1') + "/api/v2",
			"private_key": priv_key1,
			"keyID": key_id1,
			"pubKey": node_pub_key1,
			"tcp_address": "localhost:" + request.config.getoption('--tcpPort1'),
			"api_address": "http://localhost:" + request.config.getoption('--httpPort1'),
			"db":
			{
				"dbHost": request.config.getoption('--dbHost'),
				"dbName": request.config.getoption('--dbName1'),
				"login": request.config.getoption('--dbUser'),
				"pass": request.config.getoption('--dbPassword')
				}
		},
		{
			"url": "http://localhost:" + request.config.getoption('--httpPort2') + "/api/v2",
			"private_key": priv_key2,
			"keyID": key_id2,
			"pubKey": node_pub_key2,
			"tcp_address": "localhost:" + request.config.getoption('--tcpPort2'),
			"api_address": "http://localhost:" + request.config.getoption('--httpPort2'),
			"db":
			{
				"dbHost": request.config.getoption('--dbHost'),
				"dbName": request.config.getoption('--dbName2'),
				"login": request.config.getoption('--dbUser'),
				"pass": request.config.getoption('--dbPassword')
				}
		},
		{
			"url": "http://localhost:" + request.config.getoption('--httpPort3') + "/api/v2",
			"private_key": priv_key3,
			"keyID": key_id3,
			"pubKey": node_pub_key3,
			"tcp_address": "localhost:" + request.config.getoption('--tcpPort3'),
			"api_address": "http://localhost:" + request.config.getoption('--httpPort3'),
			"db":
			{
				"dbHost": request.config.getoption('--dbHost'),
				"dbName": request.config.getoption('--dbName3'),
				"login": request.config.getoption('--dbUser'),
				"pass": request.config.getoption('--dbPassword')
			}
		}]

	# Update config for tests
	conf_path = os.path.join(curDir+ '/../', 'nodesConfig.json')

	with open(conf_path, 'w') as fconf:
		fconf.write(json.dumps(config))

	print("Nodes successfully started")

if __name__ == "__main__":
    test_three_nodes()
