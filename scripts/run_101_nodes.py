import subprocess
import time
import os
import json
import argparse
import shutil
import sys

from libs import actions, tools, check

module_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.split(module_dir)[0]
libs_path = os.path.join(libs_dir, 'libs')
sys.path.insert(0, libs_path)
import loger


log = loger.create_loger(__name__, 'environment.log')
log.info('Start ' + __file__)

curDir = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()

parser.add_argument('-binary', required=True)
parser.add_argument('-workDir', default=os.path.join(curDir, 'data'))

parser.add_argument('-dbHost', default='localhost')
parser.add_argument('-dbPort', default='5432')
parser.add_argument('-dbUser', default='postgres')
parser.add_argument('-dbPassword', default='postgres')

parser.add_argument('-tcpPort1', default='7078')
parser.add_argument('-httpPort1', default='7079')
parser.add_argument('-dbName1', default='gen1')

parser.add_argument('-gapBetweenBlocks', default='2')
parser.add_argument('-centrifugo', required=True)
parser.add_argument('-test', default='true')
parser.add_argument('-wait', default='3')


args = parser.parse_args()

wait = int(args.wait)

binary = os.path.abspath(args.binary)
workDir = os.path.abspath(args.workDir)
workDir1 = os.path.join(workDir, 'node1')
firstBlockPath = os.path.join(workDir, '1block')

if os.path.exists(workDir):
    shutil.rmtree(workDir)
os.makedirs(workDir1)
log.info('Work dirs created')

#TODO maybe don't need centrifugo
# Set centrifugo variables
centrifugo_secret = '4597e75c-4376-42a6-8c1f-7e3fc7eb2114'
centrifugo_url = 'http://127.0.0.1:8000'
cenConfig = os.path.join(args.centrifugo, 'config.json')
cenPath = os.path.join(args.centrifugo, 'centrifugo')
log.info('Setted centrifugo variables')

# Create config for centrifugo
cen_config_string = {
    'secret': centrifugo_secret,
    'admin_secret': 'admin'
}
with open(cenConfig, 'w') as cen_conf_file:
    json.dump(cen_config_string, cen_conf_file, indent=4)
log.info('Created centrifugo config')

# Run centrifugo
if sys.platform == 'win32':
    centrifugo = subprocess.Popen([
        cenPath,
        '--config='+cenConfig,
        '--admin',
        '--insecure_admin',
        '--web'
    ])
else:
    centrifugo = subprocess.Popen([
        cenPath,
        '--config='+cenConfig,
        '--admin',
        '--admin_insecure'
    ])
log.info('Runned centrifugo')

time.sleep(wait)

# Generate config for first node
config1 = subprocess.Popen([
    binary,
    'config',
    '--dataDir='+workDir1,
    '--firstBlock='+firstBlockPath,
    '--dbPassword='+args.dbPassword,
    '--centUrl='+centrifugo_url,
    '--centSecret='+centrifugo_secret,
    '--dbName='+args.dbName1
])
log.info('Generated config for first node')
time.sleep(wait)

# Generate keys for first block
keys1 = subprocess.Popen([
    binary,
    'generateKeys',
    '--config='+workDir1+'/config.toml'
])
log.info('Generate keys for first block')
time.sleep(wait)

# Generate first block
first_block = subprocess.Popen([
    binary,
    'generateFirstBlock',
    '--config='+workDir1+'/config.toml',
    '--test='+args.test
])
log.info('First block generated')
time.sleep(wait)

# Init data base
first_block = subprocess.Popen([
    binary,
    'initDatabase',
    '--config='+workDir1+'/config.toml'
])
log.info('DB for first node is initialized')
time.sleep(wait)

# Start first node
start_first_node = subprocess.Popen([
    binary,
    'start',
    '--config='+workDir1+'/config.toml'
])
log.info('First node started')
time.sleep(wait)

#installing apps for first node
conf = tools.read_config('nodes')
url = conf[0]['url']
pr_key1 = conf[0]['private_key']
data = actions.login(url, pr_key1, 0)
token1 = data['jwtToken']

actions.imp_app('system', url, pr_key1, token1)
actions.imp_app('conditions', url, pr_key1, token1)
actions.imp_app('basic', url, pr_key1, token1)
actions.imp_app('lang_res', url, pr_key1, token1)

actions.roles_install(url, pr_key1, token1)

actions.voting_templates_install(url, pr_key1, token1)
actions.edit_app_param('voting_sysparams_template_id', 2, url, pr_key1, token1)
node1 = json.dumps({'tcp_address': conf[0]['tcp_address'],
                    'api_address': conf[0]['api_address'],
                    'key_id': conf[0]['keyID'],
                    'public_key': conf[0]['pubKey']})
actions.edit_app_param('first_node', node1, url, pr_key1, token1)

with open(os.path.join(workDir1, 'PrivateKey'), 'r') as f:
    priv_key1 = f.read()
with open(os.path.join(workDir1, 'PublicKey'), 'r') as f:
    pubKey1 = f.read()
with open(os.path.join(workDir1, 'KeyID'), 'r') as f:
    key_id1 = f.read()
with open(os.path.join(workDir1, 'NodePublicKey'), 'r') as f:
    node_pub_key1 = f.read()

a = 2

while a < 103:
    os.makedirs(workDir + str(a))
    # Generate config for node
    generate_config = subprocess.Popen([
        binary,
        'config',
        '--dataDir=' + workDir + str(a),
        '--firstBlock=' + firstBlockPath,
        '--dbName=' + "gen" + str(a),
        '--tcpPort=' + str(9000 + a),
        '--httpPort=' + str(1000 + a),
        '--firstBlock=' + firstBlockPath,
        '--dbPassword=' + args.dbPassword,
        '--centUrl=' + centrifugo_url,
        '--centSecret=' + centrifugo_secret,
        '--nodesAddr=' + '127.0.0.1:' + str(9000 + a)
    ])
    log.info('Generated config for ' + str(a) + 'node')
    time.sleep(wait)

    # Generate keys for node
    generateKeys = subprocess.Popen([
        binary,
        'generateKeys',
        '--config=' + workDir + str(a) + '/config.toml'
    ])
    log.info('Generated keys for ' + str(a) + 'node')
    time.sleep(wait)

    init_db_for_node = subprocess.Popen([
        binary,
        'initDatabase',
        '--config=' + workDir + str(a) + '/config.toml'
    ])
    log.info('DB for ' + str(a) + 'node is initialized')
    time.sleep(wait)

    # Start node
    start_node = subprocess.Popen([
        binary,
        'start',
        '--config=' + workDir + str(a) + '/config.toml'
    ])
    log.info('Node' + str(a) + 'started')
    time.sleep(wait)

    with open(os.path.join(workDir + str(a), 'PrivateKey'), 'r') as f:
        priv_key = f.read()
    with open(os.path.join(workDir + str(a), 'PublicKey'), 'r') as f:
        pubKey = f.read()
    with open(os.path.join(workDir + str(a), 'KeyID'), 'r') as f:
        key_id = f.read()
    with open(os.path.join(workDir + str(a), 'NodePublicKey'), 'r') as f:
        node_pub_key = f.read()

    config = [
        {
            'url': 'http://localhost:' + args.httpPort1 + '/api/v2',
            'private_key': priv_key,
            'keyID': key_id,
            'pubKey': node_pub_key,
            'tcp_address': 'localhost:' + str(9000 + a),
            'api_address': 'http://localhost:' + str(10000 + a),
            'db':
                {
                    'dbHost': args.dbHost,
                    'dbName': 'gen' + str(a),
                    'login': args.dbUser,
                    'pass': args.dbPassword
                }
        }]

    # Update config for tests
    confPath = os.path.join(curDir + '/../', 'nodesConfig.json')

    with open(confPath, 'w') as fconf:
        fconf.write(json.dumps(config, indent=4))
    log.info('Updated file nodesConfig.json')
    time.sleep(wait)

    #compare
    check.compare_nodes(config)

    #TODO voting increment nodes, need login and voting


    #Start locust
    start_locust = subprocess.Popen("locust --locustfile=trx_load.py --host=http://localhost:" +
                                    str(1000 + a) + "/api/v2 --no-web")

    a = a + 1
    #TODO loging all.



log.info('Nodes successfully started and linked')