### Installation tests for block_chain

```
git clone https://github.com/EGaaS/apla-tests.git tests
virtualenv -p python3 tests
cd tests
source bin/activate
pip install -r requirements.txt
python block_chain_test.py -v
```

### hostConfig.json
For each node:
* url:url of api
* private_key:private key of user
* dbHost: host name of data base
* dbName: name of data base
* login: login of data base,
* pass: password of data base,
* time_wait_tx_in_block:time in seconds to wait, while transaction will be writed to block 

### Installation contract functions tests

```
git clone https://github.com/EGaaS/apla-tests.git tests
virtualenv -p python3 tests
cd tests
source bin/activate
pip install -r  requirements.txt
python contract_functions_tests.py -v
```

### Config

* url:url of api
* private_key:private key of user
* time_wait_tx_in_block:time in seconds to wait, while transaction will be writed to block

### Installation contract functions tests

```
git clone https://github.com/EGaaS/apla-tests.git tests
virtualenv -p python3 tests
cd tests
source bin/activate
pip install -r  requirements.txt
python tests_API.py -v
```

### Config

* url:url of api
* private_key:private key of user
* time_wait_tx_in_block:time in seconds to wait, while transaction will be writed to block


### Launch Updating system_parameters.full_nodes

'''
git clone https://github.com/EGaaS/apla-tests.git tests
virtualenv -p python3 tests
cd tests
source bin/activate
pip install -r requirements.txt
python updateFullNode.py PrivateKey1 KeyID1 NodePublicKey1 KeyID2 NodePublicKey2 host1 httpPort1 host2 tcpPort2 

if script retuns "OK", it means that system_parameters.full_nodes updated succesfully. 
