import requests
import time

with open('D:/apla-go/PrivateKey', 'r') as f:
        prKey1 = f.read()
        print(prKey1)
with open('D:/apla2/PrivateKey', 'r') as f:
        prKey2 = f.read()
        print(prKey2)
with open('D:/apla-go/KeyID', 'r') as f:
        keyID1 = f.read()
        print(keyID1)
with open('D:/apla-go/NodePublicKey', 'r') as f:
        pubKey1 = f.read()
        print(pubKey1)
with open('D:/apla2/NodePublicKey', 'r') as f:
        pubKey2 = f.read()
        print(pubKey2)
with open('D:/apla2/KeyID', 'r') as f:
        keyID2 = f.read()
        print(keyID2)
newVal = '[[\"127.0.0.1\",\"' + keyID1 + '\",\"' + pubKey1 + '\"],[\"127.0.0.1:7081\",\"' + keyID2 + '\",\"' + pubKey2 + '\"]]'
print(newVal)
baseUrl = "http://127.0.0.1:7079/api/v2"
respUid = requests.get(baseUrl + '/getuid')
resultGetuid = respUid.json()
print(resultGetuid)

respSignTest = requests.post(baseUrl + '/signtest/', params={'forsign': resultGetuid['uid'], 'private': prKey1})
resultSignTest = respSignTest.json()
print(resultSignTest)

fullToken = 'Bearer ' + resultGetuid['token']
respLogin = requests.post(baseUrl +'/login', params={'pubkey': resultSignTest['pubkey'], 'signature': resultSignTest['signature']}, headers={'Authorization': fullToken})
resultLogin = respLogin.json()
print(resultLogin)
address = resultLogin["address"]
timeToken = resultLogin["refresh"]
jvtToken = 'Bearer ' + resultLogin["token"]
print(jvtToken)

dataCont = {"Name": "full_nodes", "Value" : newVal}
resPrepareCall = requests.post(baseUrl +'/prepare/UpdateSysParam', data=dataCont, headers={'Authorization': jvtToken})
jsPrepareCall = resPrepareCall.json()
print(jsPrepareCall)

respSignTestPCall = requests.post(baseUrl + '/signtest/', params={'forsign': jsPrepareCall['forsign'], 'private': prKey1})
resultSignTestPCall = respSignTestPCall.json()
print(resultSignTestPCall)

sign_resCall = {"time": jsPrepareCall['time'], "signature": resultSignTestPCall['signature']}
dataCont.update(sign_resCall)
print(dataCont)
respCall = requests.post(baseUrl + '/contract/UpdateSysParam', data=dataCont, headers={"Authorization": jvtToken})
resultCallContract = respCall.json()
print(resultCallContract)
time.sleep(10)
statusCall = requests.get(baseUrl + '/txstatus/' + resultCallContract["hash"], headers={"Authorization": jvtToken})
statusCallJ = statusCall.json()
print(statusCallJ)



		