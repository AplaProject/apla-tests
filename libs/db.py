import random
import string
import requests
import psycopg2
import json
import time

from collections import Counter
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key
from gevent.resolver.cares import result


class Db(object):
    def submit_query(self, query, db):
        connect = psycopg2.connect(host=db["dbHost"], dbname=db["dbName"],
                                   user=db["login"], password=db["pass"])
        cursor = connect.cursor()
        cursor.execute(query)
        return cursor.fetchall()    
        
    def compare_keys_cout(self, db):
        query = "SELECT key_id FROM block_chain Order by id DESC LIMIT 10"
        keys = self.submit_query(query, db)
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

    def compare_node_positions(self, db, maxBlockId, nodes):
        count_rec = nodes * 3 + nodes
        minBlock = maxBlockId - count_rec + 1
        request = "SELECT node_position, count(node_position) FROM block_chain WHERE id>" + str(
            minBlock) + " AND id<" + str(maxBlockId) + "GROUP BY node_position"
        positions = self.submit_query(request, db)
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

    def check_for_missing_node(self, db, minBlockId, maxBlockId):
        request = "SELECT node_position FROM block_chain WHERE id>=" + str(minBlockId) + " AND id<=" + str(maxBlockId)
        positions = self.submit_query(request, db)
        i = 0
        while i < len(positions):
            if positions[i][0] == 2:
                return False
            i = i + 1
        return True

    def isCountTxInBlock(self, db, maxBlockId, countTx):
        minBlock = maxBlockId - 3
        request = "SELECT id, tx FROM block_chain WHERE id>" + str(minBlock) + " AND id<" + str(maxBlockId)
        tx = self.submit_query(request, db)
        i = 0
        while i < len(tx):
            if tx[i][1] > countTx:
                print("Block " + str(tx[i][0]) + " contains " + \
                      str(tx[i][1]) + " transactions")
                return False
            i = i + 1
        return True
    
    def get_count_records_block_chain(self, db):
        request = "SELECT count(*) FROM \"block_chain\""
        return self.submit_query(request, db)

    def get_ten_items(self, db):
        request = "SELECT * FROM block_chain Order by id DESC LIMIT 10"
        return self.submit_query(request, db)

    def getEcosysTables(self, db):
        request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'"
        tables = self.submit_query(request, db)
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def getEcosysTablesById(self, db, ecosystemID):
        request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '" +\
            str(ecosystemID) + "_%'"
        tables = self.submit_query(request, db)
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def getCountTable(self, db, table):
        request = "SELECT count(*) FROM \"" + table + "\""
        return self.submit_query(request, db)

    def getMaxIdFromTable(self, db, table):
        request = "SELECT MAX(id) FROM \"" + table + "\""
        result = self.submit_query(request, db)
        return result[0][0]

    def executeSQL(self, db, query):
        return self.submit_query(query, db)

    def getObjectIdByName(self, db, table, name):
        request = "SELECT id FROM \"" + table + "\" WHERE name = '" + str(name) + "'"
        result = self.submit_query(request, db)
        return result[0][0]

    def getFounderId(self, db):
        request = "SELECT value FROM \"1_parameters\" WHERE name = 'founder_account'"
        result = self.submit_query(request, db)
        return result[0][0]

    def getSystemParameterValue(self, db, name):
        request = "SELECT value FROM \"1_system_parameters\" WHERE name = '" + name + "'"
        result = self.submit_query(request, db)
        return result[0][0]

    def getExportAppData(self, db, app_id, member_id):
        request = "SELECT data as TEXT FROM \"1_binaries\" WHERE name = 'export' AND app_id = " + str(
            app_id) + " AND member_id = " + str(member_id)
        result = self.submit_query(request, db)
        return result[0][0]

    def getImportAppData(self, db, member_id):
        request = "SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND member_id = " + str(member_id)
        result = self.submit_query(request, db)
        return cursor.fetchall()[0][0]

<<<<<<< HEAD
    def get_count_DB_objects(self, dbHost, dbName, login, password):
=======
    def getCountDBObjects(self, db):
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        tablesCount = {}
        tables = self.getEcosysTables(db)
        for table in tables:
            tablesCount[table[2:]] = self.getCountTable(db, table)
        return tablesCount

    def getTableColumnNames(self, db, table):
        query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
                table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
        col = {}
        col = self.submit_query(query, db)
        return col

    def getUserTableState(self, db, userTable):
        request = "SELECT * FROM \"" + userTable + "\""
        res = self.submit_query(request, db)
        col = self.getTableColumnNames(db, userTable)
        table = {}
        for i in range(len(col)):
            table[col[i][0]] = res[0][i]
        return table

<<<<<<< HEAD
    def get_user_token_amounts(self, dbHost, dbName, login, password):
=======
    def getUserTokenAmounts(self, db):
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        request = "select amount from \"1_keys\" ORDER BY amount"
        return self.submit_query(request, db)

    def get_blockchain_hash(self, db, maxBlockId):
        request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
            maxBlockId) + " ORDER BY id) AS t"
        return self.submit_query(request, db)

    def get_system_parameter(self, db, parameter):
        request = "select value from \"1_system_parameters\" WHERE name='" + parameter + "'"
        value = self.submit_query(request, db)
        return value[0][0]

    def get_commission_wallet(self, db, ecosId):
        request = "select value from \"1_system_parameters\" where name='commission_wallet'"
        wallets = self.submit_query(request, db)
        wallet = json.loads(wallets[0][0])[0][1]
        return wallet

    def get_balance_from_db(self, dbHost, dbName, login, password, keyId):
        request = "select amount from \"1_keys\" WHERE id=" + keyId
        amount = self.submit_query(request, db)
        balance = amount[0][0]
        return balance

    def get_balance_from_db_by_pub(self, db, pub):
        request = "select amount from \"1_keys\" WHERE pub='\\x" + pub + "'"
        amount = self.submit_query(request, db)
        return amount[0][0]

    def is_wallet_created(self, db, pub):
        request = "select amount from \"1_keys\" WHERE id='" + pub + "'"
        wallet = self.submit_query(request, db)
        if len(wallet) == 1 and wallet[0][0] == 1000000000000000000000:
            return True
        else:
            return False

    def get_block_gen_node(self, db, block):
        request = "select node_position from \"block_chain\" WHERE id=" + block
        nodes = self.submit_query(request, db)
        return nodes[0][0]

    def isCommissionInHistory(self, db, idFrom, idTo, summ):
        request = "select * from \"1_history\" WHERE sender_id=" + idFrom + \
                       " AND recipient_id=" + str(idTo) + " AND amount=" + str(summ)
        rec = self.submit_query(request, db)
        if len(rec) > 0:
            return True
        else:
            return False