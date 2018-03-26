import requests
import time
import argparse

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

	respSignTest = requests.post(baseUrl + '/signtest/', params={'forsign': resultGetuid['uid'], 'private': args.privKey})
	resultSignTest = respSignTest.json()

	fullToken = 'Bearer ' + resultGetuid['token']
	respLogin = requests.post(baseUrl +'/login', params={'pubkey': resultSignTest['pubkey'], 'signature': resultSignTest['signature']}, headers={'Authorization': fullToken})
	resultLogin = respLogin.json()
	address = resultLogin["address"]
	timeToken = resultLogin["refresh"]
	jvtToken = 'Bearer ' + resultLogin["token"]

	print(args.name)
	print(args.value)
	dataCont = {"Name": args.name, "Value" : args.value}
	resPrepareCall = requests.post(baseUrl +'/prepare/UpdateSysParam', data=dataCont, headers={'Authorization': jvtToken})
	jsPrepareCall = resPrepareCall.json()

	respSignTestPCall = requests.post(baseUrl + '/signtest/', params={'forsign': jsPrepareCall['forsign'], 'private': args.privKey})
	resultSignTestPCall = respSignTestPCall.json()
	sign_resCall = {"time": jsPrepareCall['time'], "signature": resultSignTestPCall['signature']}
	dataCont.update(sign_resCall)
	respCall = requests.post(baseUrl + '/contract/UpdateSysParam', data=dataCont, headers={"Authorization": jvtToken})
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