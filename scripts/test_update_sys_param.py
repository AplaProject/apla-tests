import requests
import time
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

def test_update_sys_param(request):

	baseUrl = "http://"+request.config.getoption('--httpHost1')+":"+request.config.getoption('--httpPort1')+"/api/v2"
	respUid = requests.get(baseUrl + '/getuid')
	resultGetuid = respUid.json()

	signature = sign(request.config.getoption('--privKey'), "LOGIN" + resultGetuid['uid'])
	print("signature------------", signature)

	fullToken = 'Bearer ' + resultGetuid['token']
	respLogin = requests.post(baseUrl +'/login', params={'pubkey': get_public_key(request.config.getoption('--privKey')),
														 'signature': signature}, headers={'Authorization': fullToken})
	resultLogin = respLogin.json()
	address = resultLogin["address"]
	timeToken = resultLogin["refresh"]
	jvtToken = 'Bearer ' + resultLogin["token"]

	print(args.name)
	print(args.value)
	dataCont = {"Name": request.config.getoption('--name'), "Value" : request.config.getoption('--value')}
	resPrepareCall = requests.post(baseUrl +'/prepare/UpdateSysParam', data=dataCont,
								   headers={'Authorization': jvtToken})
	jsPrepareCall = resPrepareCall.json()

	signatureP = sign(args.privKey, jsPrepareCall['forsign'])
	print("signatureP-------------", signatureP)
	sign_resCall = {"time": jsPrepareCall['time'], "signature": signatureP}
	respCall = requests.post(baseUrl + '/contract/' + jsPrepareCall['request_id'], data=sign_resCall,
							 headers={"Authorization": jvtToken})
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