import os
import json

def test_update_private_key_for_run_tests(request):

	with open(os.path.join(request.config.getoption('--privateKeyPath'), 'PrivateKey'), 'r') as f:
		privKey1 = f.read()

	file = os.path.join(request.config.getoption('--configPath'), "hostConfig.json")
	with open(file, 'r') as f:
		data = f.read()
		lines = json.loads(data)

	# Update private keys in config
	lines["1"]["private_key"] = privKey1
	lines["2"]["private_key"] = privKey1
	lines["3"]["private_key"] = privKey1

	# Update url in config
	lines["2"]["url"] = lines["1"]["url"]
	lines["3"]["url"] = lines["1"]["url"]

	# Update DB name in config
	lines["1"]["dbName"] = request.config.getoption('--dbName1')
	lines["2"]["dbName"] = request.config.getoption('--dbName1')
	lines["3"]["dbName"] = request.config.getoption('--dbName1')

	with open(file, 'w') as f:
		json.dump(lines, f)

	print("hostConfig.json is updated!")


