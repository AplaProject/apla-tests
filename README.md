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

### Installation Api test V1

```
git clone https://github.com/EGaaS/apla-tests.git tests
virtualenv -p python3 tests
cd tests
source bin/activate
pip install -r requirements.txt
python tests.py -v
```

### Config

* url:url of api
* state:id of state
* private_key:private key of user
* time_wait_tx_in_block:time in seconds to wait, while transaction will be writed to block
