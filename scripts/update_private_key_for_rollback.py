import os

def test_update_private_key_for_rollback(request):

	with open(os.path.join(request.config.getoption('--privateKeyPath'), 'PrivateKey'), 'r') as f:
		privKey1 = f.read()

	config = os.path.join(request.config.getoption('--configPath'), 'config.json')
	with open(config) as fconf:
		lines = fconf.readlines()

	# Update private keys in config
	del lines[2]
	lines.insert(2, "\t\t\"private_key\": \""+privKey1+"\",\n")

	# Update DB name in config
	del lines[5]
	lines.insert(5, "\t\t\"dbName\": \""+request.config.getoption('--dbName1')+"\",\n")

	with open(config, 'w') as fconf:
		fconf.write(''.join(lines))

	print("config.json is updated!")