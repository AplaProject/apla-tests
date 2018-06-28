import requests
import time
import argparse
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('-privKey', required=True)
	parser.add_argument('-name', required=True)
	parser.add_argument('-value', required=True)

	parser.add_argument('-httpHost', default='127.0.0.1')
	parser.add_argument('-httpPort', default='7079')

	args = parser.parse_args()

	baseUrl = "http://"+args.httpHost+":"+args.httpPort+"/api/v2"
	respUid = requests.get(baseUrl + '/getuid')
	resultGetuid = respUid.json()

	signature = sign(args.privKey, "LOGIN" + resultGetuid['uid'])
	print("signature------------", signature)

	fullToken = 'Bearer ' + resultGetuid['token']
	respLogin = requests.post(baseUrl +'/login', params={'pubkey': get_public_key(args.privKey), 'signature': signature}, headers={'Authorization': fullToken})
	resultLogin = respLogin.json()
	address = resultLogin["address"]
	timeToken = resultLogin["refresh"]
	jvtToken = 'Bearer ' + resultLogin["token"]

	print(args.name)
	print(args.value)
	dataCont = {"Name": args.name, "Value" : args.value}
	resPrepareCall = requests.post(baseUrl +'/prepare/UpdateSysParam', data=dataCont, headers={'Authorization': jvtToken})
	jsPrepareCall = resPrepareCall.json()

	signatureP = sign(args.privKey, jsPrepareCall['forsign'])
	print("signatureP-------------", signatureP)
	sign_resCall = {"time": jsPrepareCall['time'], "signature": signatureP}
	respCall = requests.post(baseUrl + '/contract/' + jsPrepareCall['request_id'], data=sign_resCall, headers={"Authorization": jvtToken})
	resultCallContract = respCall.json()
	time.sleep(25)
	statusCall = requests.get(baseUrl + '/txstatus/' + resultCallContract["hash"], headers={"Authorization": jvtToken})
	statusCallJ = statusCall.json()
	print(statusCallJ)
	print(statusCallJ["blockid"])
	if len(statusCallJ["blockid"]) > 0:
		print("OK")
	else:
		print("Error: system parameter is not updated")
		exit(1)