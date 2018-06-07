import requests
import time
import sys
from random import choice
from string import ascii_uppercase
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


if __name__ == "__main__":
	if len (sys.argv) < 6:
		print ("Error: Too few parameters")
		exit(1)
	else:
		prKey1 = sys.argv[1]
		host1 = sys.argv[2]
		httpPort1 = sys.argv[3]
		id = sys.argv[4]
		pub = sys.argv[5]
		amount = sys.argv[6]
		baseUrl = "http://"+host1+":"+httpPort1+"/api/v2"
		respUid = requests.get(baseUrl + '/getuid')
		resultGetuid = respUid.json()

		signature = sign(prKey1, "LOGIN" + resultGetuid['uid'])
		print("sign----", signature, "prKey---", prKey1, "data---", "LOGIN" + resultGetuid['uid'])

		fullToken = 'Bearer ' + resultGetuid['token']
		respLogin = requests.post(baseUrl +'/login', params={'pubkey': get_public_key(prKey1), 'signature': signature}, headers={'Authorization': fullToken})
		resultLogin = respLogin.json()
		address = resultLogin["address"]
		timeToken = resultLogin["refresh"]
		jvtToken = 'Bearer ' + resultLogin["token"]
		
		contName = 'con_' + ''.join(choice(ascii_uppercase) for i in range(12))
		code = '{data {}conditions {} action {$result=DBInsert(\"keys\", \"id,pub,amount\", \"' + id + '\", \"' + pub + '\", \"' + amount + '\") }}'
		updateKeysCode = 'contract '+contName+code
		dataContKeys = {'ApplicationId': 1,'Wallet': '', 'Value': updateKeysCode, 'Conditions': """ContractConditions(`MainCondition`)"""}
		print("-------------------------------")
		resPrepareCall = requests.post(baseUrl +'/prepare/NewContract', data=dataContKeys, headers={'Authorization': jvtToken})
		jsPrepareCall = resPrepareCall.json()
		print(jsPrepareCall)
		print("-------------------------------")
		signatureCall = sign(prKey1, jsPrepareCall['forsign'])
		print("sign----", signatureCall, "prKey---", prKey1, "data---", jsPrepareCall['forsign'])

		sign_resCall = {"time": jsPrepareCall['time'], "signature": signatureCall}
		respCall = requests.post(baseUrl + '/contract/' + jsPrepareCall['request_id'], data=sign_resCall, headers={"Authorization": jvtToken})
		resultCallContract = respCall.json()
		print(resultCallContract)
		time.sleep(20)
		statusCall = requests.get(baseUrl + '/txstatus/' + resultCallContract["hash"], headers={"Authorization": jvtToken})
		statusCallJ = statusCall.json()
		print(statusCallJ)
		if len(statusCallJ["blockid"]) > 0:
			print("Conract updateKeys created")
		else:
			print("Error: Conract didn't updateKeys create")
		
		dataCont = {}
		print("-------------------------------")
		resPrepareCall2 = requests.post(baseUrl +'/prepare/' + contName, data=dataCont, headers={'Authorization': jvtToken})
		jsPrepareCall2 = resPrepareCall2.json()
		print(jsPrepareCall2)
		print("-------------------------------")
		signatureCallP = sign(prKey1, jsPrepareCall2['forsign'])
		print("sign------", signatureCallP, "prKey1----", prKey1, "data-----", jsPrepareCall2['forsign'])

		sign_resCall = {"time": jsPrepareCall2['time'], "signature": signatureCallP}
		respCall = requests.post(baseUrl + '/contract/' + jsPrepareCall2['request_id'], data=sign_resCall, headers={"Authorization": jvtToken})
		resultCallContract = respCall.json()
		print("-------------------------------------------------------------------------")
		print(resultCallContract)
		time.sleep(20)
		statusCall = requests.get(baseUrl + '/txstatus/' + resultCallContract["hash"], headers={"Authorization": jvtToken})
		statusCallJ = statusCall.json()
		print(statusCallJ)
		if len(statusCallJ["blockid"]) > 0:
			print("OK")
			exit(0)
		else:
			print("Error: Keys is not updated")
			exit(1)
