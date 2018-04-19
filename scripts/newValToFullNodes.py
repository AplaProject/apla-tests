import requests
import time
import sys

if __name__ == "__main__":
	if len (sys.argv) < 4:
		print ("Error: Too few parameters")
		exit(1)
	else:
		prKey1 = sys.argv[1]
		host1 = sys.argv[2]
		httpPort1 = sys.argv[3]
		newVal = sys.argv[4]
		print(newVal)
		baseUrl = "http://"+host1+":"+httpPort1+"/api/v2"
		respUid = requests.get(baseUrl + '/getuid')
		resultGetuid = respUid.json()

		respSignTest = requests.post(baseUrl + '/signtest/', params={'forsign': resultGetuid['uid'], 'private': prKey1})
		resultSignTest = respSignTest.json()
		print(resultSignTest)

		fullToken = 'Bearer ' + resultGetuid['token']
		respLogin = requests.post(baseUrl +'/login', params={'pubkey': resultSignTest['pubkey'], 'signature': resultSignTest['signature']}, headers={'Authorization': fullToken})
		resultLogin = respLogin.json()
		address = resultLogin["address"]
		timeToken = resultLogin["refresh"]
		jvtToken = 'Bearer ' + resultLogin["token"]

		dataCont = {"Name": "full_nodes", "Value" : newVal}
		print("-------------------------------")
		resPrepareCall = requests.post(baseUrl +'/prepare/UpdateSysParam', data=dataCont, headers={'Authorization': jvtToken})
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
			exit(0)
			print("OK")
		else:
			exit(1)
			print("Error: fullNodes is not updated")