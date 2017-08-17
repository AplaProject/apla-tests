### Installation

git clone https://github.com/EGaaS/apla-tests.git tests
virtualenv -p python3 tests
cd tests
source bin/activate
pip install -r requirements.txt
python tests.py -v

### Config

url:url of api
state:id of state
private_key:private key of user
time_wait_tx_in_block:time in seconds to wait, while transaction will be writed to block
