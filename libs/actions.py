import random
import string
import requests
import psycopg2
import json
import time

from collections import Counter
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key


class Actions(object):
    '''
    def __init__(self):
        global url, token, prKey, pause, dbHost, dbName, login, pas
        self.config = config.getNodeConfig()
        url = self.config["1"]["url"]
        pause = self.config["1"]["time_wait_tx_in_block"]
        prKey = self.config["1"]['private_key']
        dbHost = self.config["1"]["dbHost"]
        dbName = self.config["1"]['dbName']
        login = self.config["1"]["login"]
        pas = self.config["1"]['pass']
        self.data = utils.login(url, prKey, 0)
        token = self.data["jwtToken"]
        self.db_query = DatabaseQueries()



    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash", result)
        hash = result['hash']
        status = utils.tx_status(url, pause, hash, jwtToken)
        if len(status['blockid']) > 0:
            self.assertNotIn(json.dumps(status), 'errmsg')
            return {"blockid": int(status["blockid"]), "error": "0"}
        else:
            return {"blockid": 0, "error": status["errmsg"]["error"]}

    def call(self, name, data):
        resp = utils.call_contract(url, prKey, name, data, token)
        resp = self.assertTxInBlock(resp, token)
        return resp

    def assertMultiTxInBlock(self, result, jwtToken):
        self.assertIn("hashes", result)
        hashes = result['hashes']
        result = utils.tx_status_multi(url, pause, hashes, jwtToken)
        for status in result.values():
            self.assertNotIn('errmsg', status)
            self.assertGreater(int(status["blockid"]), 0,
                               "BlockID not generated")

    def callMulti(self, name, data, sleep=0):
        resp = utils.call_multi_contract(url, prKey, name, data, token)
        time.sleep(sleep)
        resp = self.assertMultiTxInBlock(resp, token)
        return resp

    def waitBlockId(self, old_block_id, limit):
        while True:
            # add contract, which get block_id
            body = "{\n data{} \n conditions{} \n action { \n  $result = $block \n } \n }"
            code, name = utils.generate_name_and_code(body)
            data = {"Value": code, "ApplicationId": 1,
                    "Conditions": "true"}
            res = self.call("NewContract", data)
            self.assertGreater(res["blockid"], 0, "BlockId is not generated: " + str(res))
            currrent_block_id = res["blockid"]
            expected_block_id = old_block_id + limit + 1  # +1 spare block
            if currrent_block_id == expected_block_id:
                break
    '''

    def get_uid(url):
        resp = requests.get(url + '/getuid')
        result = resp.json()
        return result['token'], result['uid']

    def login(url, prKey, role=0, ecosystem=1):
        token, uid = Actions.get_uid(url)
        signature = sign(prKey, "LOGIN" + uid)
        pubkey = get_public_key(prKey)
        fullToken = 'Bearer ' + token
        data = {'pubkey': pubkey, 'signature': signature, "role_id": role, "ecosystem": ecosystem}
        head = {'Authorization': fullToken}
        resp = requests.post(url + '/login', params=data, headers=head)
        res = resp.json()
        result = {}
        result["uid"] = uid
        result["timeToken"] = res["refresh"]
        result["jwtToken"] = 'Bearer ' + res["token"]
        result["pubkey"] = pubkey
        result["address"] = res["address"]
        result["key_id"] = res["key_id"]
        return result

    def prepare_tx(url, prKey, entity, jvtToken, data):
        heads = {'Authorization': jvtToken}
        resp = requests.post(url + '/prepare/' + entity, data=data, headers=heads)
        result = resp.json()
        signature = sign(prKey, result['forsign'])
        return {"time": result['time'], "signature": signature, "reqID": result['request_id']}

    def prepare_tx_with_files(url, prKey, entity, jvtToken, data, files):
        heads = {'Authorization': jvtToken}
        resp = requests.post(url + '/prepare/' + entity,
                             data=data, headers=heads, files=files)
        result = resp.json()
        signature = sign(prKey, result['forsign'])
        return {"time": result['time'], "signature": signature, "reqID": result['request_id']}

    def call_contract(url, prKey, name, data, jvtToken):
        sign = Actions.prepare_tx(url, prKey, name, jvtToken, data)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        urlEnd = url + '/contract/' + sign["reqID"]
        resp = requests.post(urlEnd, data=dataContract, headers={"Authorization": jvtToken})
        result = resp.json()
        return result

    def prepare_multi_tx(url, prKey, entity, jvtToken, data):
        urlToCont = url + '/prepareMultiple/'
        heads = {'Authorization': jvtToken}
        request = {"token_ecosystem": "",
                   "max_sum": "",
                   "payover": "",
                   "signed_by": "",
                   "contracts": data}
        resp = requests.post(urlToCont, data={"data": json.dumps(request)}, headers=heads)
        result = resp.json()
        forsigns = result['forsign']
        signatures = [sign(prKey, forsign) for forsign in forsigns]
        return {"time": result['time'], "signatures": signatures, "reqID": result['request_id']}

    def call_multi_contract(url, prKey, name, data, jvtToken):
        sign = Actions.prepare_multi_tx(url, prKey, name, jvtToken, data)
        dataContract = {"time": sign['time'], "signatures": sign["signatures"]}
        urlEnd = url + '/contractMultiple/' + sign["reqID"]
        resp = requests.post(urlEnd, data={"data": json.dumps(dataContract)}, headers={"Authorization": jvtToken})
        result = resp.json()
        return result

    def call_contract_with_files(url, prKey, name, data, files, jvtToken):
        sign = Actions.prepare_tx_with_files(url, prKey, name, jvtToken, data, files)
        dataContract = {"time": sign['time'], "signature": sign["signature"]}
        urlEnd = url + '/contract/' + sign["reqID"]
        resp = requests.post(urlEnd, data=dataContract,
                             headers={"Authorization": jvtToken})
        result = resp.json()
        return result

    def tx_status(url, sleepTime, hsh, jvtToken):
        sec = 0
        urlEnd = url + '/tx_status/' + hsh
        while sec < sleepTime:
            time.sleep(1)
            resp = requests.get(urlEnd, headers={'Authorization': jvtToken})
            jresp = resp.json()
            if (len(jresp['blockid']) > 0 and 'errmsg' not in json.dumps(jresp)) or ('errmsg' in json.dumps(jresp)):
                return resp.json()
            else:
                sec = sec + 1
        return resp.json()

    def tx_status_multi(url, sleepTime, hshs, jvtToken):
        urlEnd = url + '/txstatusMultiple/'
        allTxInBlocks = False
        sec = 0
        while sec < sleepTime:
            time.sleep(1)
            resp = requests.post(urlEnd, params={"data": json.dumps({"hashes": hshs})},
                                 headers={'Authorization': jvtToken})
            jresp = resp.json()["results"]
            for status in jresp.values():
                if (len(status['blockid']) > 0 and 'errmsg' not in json.dumps(status)):
                    allTxInBlocks = True
                else:
                    allTxInBlocks = False
            if allTxInBlocks == True:
                return jresp
            else:
                sec = sec + 1
        return jresp

    def generate_random_name():
        name = []
        for _ in range(1, 30):
            sym = random.choice(string.ascii_lowercase)
            name.append(sym)
        return "".join(name)

    def generate_name_and_code(sourceCode):
        name = "Cont_" + Actions.generate_random_name()
        if sourceCode == "":
            sCode = """{data { }	conditions {	}	action {	}	}"""
        else:
            sCode = sourceCode
        code = "contract " + name + sCode
        return code, name

    def generate_code(contractName, sourceCode):
        if sourceCode == "":
            sCode = """{data { }	conditions {	}	action {	}	}"""
        else:
            sCode = sourceCode
        code = "contract " + contractName + sCode
        return code

    def compare_keys_cout(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT key_id FROM block_chain Order by id DESC LIMIT 10")
        keys = cursor.fetchall()
        firstKey = keys[1]
        secondKey = ""
        for key in keys:
            if key != firstKey:
                secondKey = key
        if secondKey == "":
            return False
        else:
            keysCounter = Counter(keys)
            firstKeyCount = keysCounter[firstKey]
            secondKeyCount = keysCounter[secondKey]
            compare = firstKeyCount - secondKeyCount
            if (compare > 1) | (compare < -1):
                return False
            else:
                return True

    def compare_node_positions(dbHost, dbName, login, password, maxBlockId, nodes):
        count_rec = nodes * 3 + nodes
        minBlock = maxBlockId - count_rec + 1
        request = "SELECT node_position, count(node_position) FROM block_chain WHERE id>" + str(
            minBlock) + " AND id<" + str(maxBlockId) + "GROUP BY node_position"
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        positions = cursor.fetchall()
        countBlocks = round(count_rec / nodes / 10 * 7)
        if len(positions) < nodes:
            print("One of nodes doesn't generate blocks" + str(positions))
            return False
        i = 0
        while i < len(positions):
            if positions[i][1] < countBlocks - 1:
                print("Node " + str(i) + " generated " + str(positions[i][1]) + " blocks:" + str(positions))
                return False
            i = i + 1
        return True

    def check_for_missing_node(dbHost, dbName, login, password, minBlockId, maxBlockId):
        request = "SELECT node_position FROM block_chain WHERE id>=" + str(minBlockId) + " AND id<=" + str(maxBlockId)
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        positions = cursor.fetchall()
        i = 0
        while i < len(positions):
            if positions[i][0] == 2:
                return False
            i = i + 1
        return True

    def is_count_tx_in_block(dbHost, dbName, login, password, maxBlockId, countTx):
        minBlock = maxBlockId - 3
        request = "SELECT id, tx FROM block_chain WHERE id>" + str(minBlock) + " AND id<" + str(maxBlockId)
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        tx = cursor.fetchall()
        i = 0
        while i < len(tx):
            if tx[i][1] > countTx:
                print("Block " + str(tx[i][0]) + " contains " + \
                      str(tx[i][1]) + " transactions")
                return False
            i = i + 1
        return True

    def get_count_records_block_chain(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT count(*) FROM \"block_chain\"")
        return cursor.fetchall()

    def get_ten_items(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM block_chain Order by id DESC LIMIT 10")
        keys = cursor.fetchall()
        return keys

    def get_ecosys_tables(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(
            "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'")
        tables = cursor.fetchall()
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def get_ecosys_tables_by_id(dbHost, dbName, login, password, ecosystemID):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(
            "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '" + str(
                ecosystemID) + "_%'")
        tables = cursor.fetchall()
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def get_count_table(dbHost, dbName, login, password, table):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT count(*) FROM \"" + table + "\"")
        return cursor.fetchall()[0][0]

    def get_max_id_from_table(dbHost, dbName, login, password, table):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT MAX(id) FROM \"" + table + "\"")
        return cursor.fetchall()[0][0]

    def execute_SQL(dbHost, dbName, login, password, query):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def get_object_id_by_name(dbHost, dbName, login, password, table, name):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT id FROM \"" + table + "\" WHERE name = '" + str(name) + "'")
        print(cursor.fetchall())
        return cursor.fetchall()[0][0]

    def get_founder_id(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT value FROM \"1_parameters\" WHERE name = 'founder_account'")
        return cursor.fetchall()[0][0]

    def get_system_parameter_value(dbHost, dbName, login, password, name):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT value FROM \"1_system_parameters\" WHERE name = '" + name + "'")
        return cursor.fetchall()[0][0]

    def get_export_app_data(dbHost, dbName, login, password, app_id, member_id):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT data as TEXT FROM \"1_binaries\" WHERE name = 'export' AND app_id = " + str(
            app_id) + " AND member_id = " + str(member_id))
        return cursor.fetchall()[0][0]

    def get_import_app_data(dbHost, dbName, login, password, member_id):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND member_id = " + str(member_id))
        return cursor.fetchall()[0][0]

    def get_count_DB_objects(dbHost, dbName, login, password):
        tablesCount = {}
        tables = Actions.get_ecosys_tables(dbHost, dbName, login, password)
        for table in tables:
            tablesCount[table[2:]] = Actions.get_count_table(dbHost, dbName, login, password, table)
        return tablesCount

    def get_table_column_names(dbHost, dbName, login, password, table):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
                table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
        cursor.execute(query)
        col = {}
        col = cursor.fetchall()
        return col

    def get_user_table_state(dbHost, dbName, login, password, userTable):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM \"" + userTable + "\"")
        res = cursor.fetchall()
        col = Actions.get_table_column_names(dbHost, dbName, login, password, userTable)
        table = {}
        for i in range(len(col)):
            table[col[i][0]] = res[0][i]
        return table

    def get_user_token_amounts(dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" ORDER BY amount")
        amounts = cursor.fetchall()
        return amounts

    def get_blockchain_hash(dbHost, dbName, login, password, maxBlockId):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
            maxBlockId) + " ORDER BY id) AS t"
        cursor.execute(request)
        hash = cursor.fetchall()
        return hash

    def get_system_parameter(dbHost, dbName, login, password, parameter):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select value from \"1_system_parameters\" WHERE name='" + parameter + "'")
        value = cursor.fetchall()
        return value[0][0]

    def get_commission_wallet(dbHost, dbName, login, password, ecosId):
        request = "select value from \"1_system_parameters\" where name='commission_wallet'"
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(request)
        wallets = cursor.fetchall()
        wallet = json.loads(wallets[0][0])[0][1]
        return wallet

    def get_balance_from_db(dbHost, dbName, login, password, keyId):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE id=" + keyId)
        amount = cursor.fetchall()
        balance = amount[0][0]
        return balance

    def get_balance_from_db_by_pub(dbHost, dbName, login, password, pub):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE pub='\\x" + pub + "'")
        amount = cursor.fetchall()
        return amount[0][0]

    def is_wallet_created(dbHost, dbName, login, password, pub):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE id='" + pub + "'")
        wallet = cursor.fetchall()
        if len(wallet) == 1 and wallet[0][0] == 1000000000000000000000:
            return True
        else:
            return False

    def get_block_gen_node(dbHost, dbName, login, password, block):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select node_position from \"block_chain\" WHERE id=" + block)
        nodes = cursor.fetchall()
        return nodes[0][0]

    def is_commission_in_history(dbHost, dbName, login, password, idFrom, idTo, summ):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select * from \"1_history\" WHERE sender_id=" + idFrom + \
                       " AND recipient_id=" + str(idTo) + " AND amount=" + str(summ))
        rec = cursor.fetchall()
        if len(rec) > 0:
            return True
        else:
            return False

    def call_get_api(url, data, token):
        resp = requests.get(url, data=data, headers={"Authorization": token})
        return resp.json()

    def call_get_api_with_full_response(url, data, token):
        resp = requests.get(url, data=data, headers={"Authorization": token})
        return resp

    def call_post_api(url, data, token):
        resp = requests.post(url, data=data, headers={"Authorization": token})
        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def get_count(self, url, type, token):
        endPoint = url + "/list/" + type
        res = self.call_get_api(endPoint, "", token)
        return res["count"]

    def get_list(self, url, type, token):
        count = self.get_count(url, type, token)
        endPoint = url + "/list/" + type + "?limit=" + count
        res = self.call_get_api(endPoint, "", token)
        return res

    def get_contract_id(self, url, name, token):
        endPoint = url + "/contract/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["tableid"]

    def get_application_id(self, url, name, token):
        id = None
        endPoint = url + "/list/applications"
        res = self.call_get_api(endPoint, "", token)
        for app in res["list"]:
            if app["name"] == name:
                id = app["id"]
        return id

    def get_object_id(self, url, name, object, token):
        id = None
        endPoint = url + "/list/" + object
        res = self.call_get_api(endPoint, "", token)
        for object in res["list"]:
            if object["name"] == name:
                id = object["id"]
        return id

    def is_contract_activated(self, url, name, token):
        endPoint = url + "/contract/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["active"]

    def get_activated_wallet(self, url, name, token):
        endPoint = url + "/contract/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["walletid"]

    def get_parameter_id(self, url, name, token):
        endPoint = url + "/ecosystemparam/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["id"]

    def get_parameter_value(self, url, name, token):
        endPoint = url + "/ecosystemparam/" + name
        res = self.call_get_api(endPoint, "", token)
        return res["value"]

    def get_content(self, url, type, name, lang, appId, token):
        if (lang != ""):
            data = {"lang": lang, "app_id": appId}
        else:
            data = ""
        endPoint = url + "/content/" + type + "/" + name
        res = self.call_post_api(endPoint, data, token)
        return res

    def get_max_block_id(self, url, token):
        data = ""
        endPoint = url + "/maxblockid"
        result = self.call_get_api(endPoint, data, token)
        return result["max_block_id"]
