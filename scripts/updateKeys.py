import requests
import time
import sys
from random import choice
from string import ascii_uppercase


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

		respSignTest = requests.post(baseUrl + '/signtest/', params={'forsign': "LOGIN" + resultGetuid['uid'], 'private': prKey1})
		resultSignTest = respSignTest.json()
		print(resultSignTest)

		fullToken = 'Bearer ' + resultGetuid['token']
		respLogin = requests.post(baseUrl +'/login', params={'pubkey': resultSignTest['pubkey'], 'signature': resultSignTest['signature']}, headers={'Authorization': fullToken})
		resultLogin = respLogin.json()
		address = resultLogin["address"]
		timeToken = resultLogin["refresh"]
		jvtToken = 'Bearer ' + resultLogin["token"]
		
		contName = 'con_' + ''.join(choice(ascii_uppercase) for i in range(12))
		code = '{data {}conditions {} action {$result=DBInsert(\"keys\", \"id,pub,amount\", \"' + id + '\", \"' + pub + '\", \"' + amount + '\") }}'
		updateKeysCode = 'contract '+contName+code
		dataContKeys = {'Wallet': '', 'Value': updateKeysCode, 'Conditions': """ContractConditions(`MainCondition`)"""}
		print("-------------------------------")
		resPrepareCall = requests.post(baseUrl +'/prepare/NewContract', data=dataContKeys, headers={'Authorization': jvtToken})
		jsPrepareCall = resPrepareCall.json()
		print(jsPrepareCall)
		print("-------------------------------")
		respSignTestPCall = requests.post(baseUrl + '/signtest/', params={'forsign': jsPrepareCall['forsign'], 'private': prKey1})
		resultSignTestPCall = respSignTestPCall.json()
		print(resultSignTestPCall)

		sign_resCall = {"time": jsPrepareCall['time'], "signature": resultSignTestPCall['signature']}
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
		resPrepareCall = requests.post(baseUrl +'/prepare/' + contName, data=dataCont, headers={'Authorization': jvtToken})
		jsPrepareCall = resPrepareCall.json()
		print(jsPrepareCall)
		print("-------------------------------")
		respSignTestPCall = requests.post(baseUrl + '/signtest/', params={'forsign': jsPrepareCall['forsign'], 'private': prKey1})
		resultSignTestPCall = respSignTestPCall.json()
		print(resultSignTestPCall)

		sign_resCall = {"time": jsPrepareCall['time'], "signature": resultSignTestPCall['signature']}
		respCall = requests.post(baseUrl + '/contract/' + jsPrepareCall['request_id'], data=sign_resCall, headers={"Authorization": jvtToken})
		resultCallContract = respCall.json()
		print(resultCallContract)
		time.sleep(20)
		statusCall = requests.get(baseUrl + '/txstatus/' + resultCallContract["hash"], headers={"Authorization": jvtToken})
		statusCallJ = statusCall.json()
		print(statusCallJ)
		if len(statusCallJ["blockid"]) > 0:
			print("OK")
			exit(0)
		else:
			print("Error: fullNodes is not updated")
			exit(1)
