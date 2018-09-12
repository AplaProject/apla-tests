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
    def submit_query(self, query, dbHost, dbName, login, password):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute(query)
        return cursor.fetchall()    
        
    def compare_keys_cout(self, dbHost, dbName, login, password):
        query = "SELECT key_id FROM block_chain Order by id DESC LIMIT 10"
        keys = self.submit_query(query, dbHost, dbName, login, password)
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

    def compare_node_positions(self, dbHost, dbName, login, password, maxBlockId, nodes):
        count_rec = nodes * 3 + nodes
        minBlock = maxBlockId - count_rec + 1
        request = "SELECT node_position, count(node_position) FROM block_chain WHERE id>" + str(
            minBlock) + " AND id<" + str(maxBlockId) + "GROUP BY node_position"
        positions = self.submit_query(request, dbHost, dbName, login, password)
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

    def check_for_missing_node(self, dbHost, dbName, login, password, minBlockId, maxBlockId):
        request = "SELECT node_position FROM block_chain WHERE id>=" + str(minBlockId) + " AND id<=" + str(maxBlockId)
        positions = self.submit_query(request, dbHost, dbName, login, password)
        i = 0
        while i < len(positions):
            if positions[i][0] == 2:
                return False
            i = i + 1
        return True

    def isCountTxInBlock(self, dbHost, dbName, login, password, maxBlockId, countTx):
        minBlock = maxBlockId - 3
        request = "SELECT id, tx FROM block_chain WHERE id>" + str(minBlock) + " AND id<" + str(maxBlockId)
        tx = self.submit_query(request, dbHost, dbName, login, password)
        i = 0
        while i < len(tx):
            if tx[i][1] > countTx:
                print("Block " + str(tx[i][0]) + " contains " + \
                      str(tx[i][1]) + " transactions")
                return False
            i = i + 1
        return True
    
    def get_count_records_block_chain(self, dbHost, dbName, login, password):
        request = "SELECT count(*) FROM \"block_chain\""
        return self.submit_query(request, dbHost, dbName, login, password)

    def get_ten_items(self, dbHost, dbName, login, password):
        request = "SELECT * FROM block_chain Order by id DESC LIMIT 10"
        return self.submit_query(request, dbHost, dbName, login, password)

    def getEcosysTables(self, dbHost, dbName, login, password):
        request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'"
        tables = self.submit_query(request, dbHost, dbName, login, password)
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def getEcosysTablesById(self, dbHost, dbName, login, password, ecosystemID):
        request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '" +\
            str(ecosystemID) + "_%'"
        tables = self.submit_query(request, dbHost, dbName, login, password)
        list = []
        i = 0
        while i < len(tables):
            list.append(tables[i][0])
            i = i + 1
        return list

    def getCountTable(self, dbHost, dbName, login, password, table):
        request = "SELECT count(*) FROM \"" + table + "\""
        return self.submit_query(request, dbHost, dbName, login, password)

    def getMaxIdFromTable(self, dbHost, dbName, login, password, table):
        request = "SELECT MAX(id) FROM \"" + table + "\""
        result = self.submit_query(request, dbHost, dbName, login, password)
        return result[0][0]

    def executeSQL(self, dbHost, dbName, login, password, query):
        return self.submit_query(query, dbHost, dbName, login, password)

    def getObjectIdByName(self, dbHost, dbName, login, password, table, name):
        request = "SELECT id FROM \"" + table + "\" WHERE name = '" + str(name) + "'"
        result = self.submit_query(request, dbHost, dbName, login, password)
        return result[0][0]

    def getFounderId(self, dbHost, dbName, login, password):
        request = "SELECT value FROM \"1_parameters\" WHERE name = 'founder_account'"
        result = self.submit_query(request, dbHost, dbName, login, password)
        return result[0][0]

    def getSystemParameterValue(self, dbHost, dbName, login, password, name):
        request = "SELECT value FROM \"1_system_parameters\" WHERE name = '" + name + "'"
        result = self.submit_query(request, dbHost, dbName, login, password)
        return result[0][0]

    def getExportAppData(self, dbHost, dbName, login, password, app_id, member_id):
        request = "SELECT data as TEXT FROM \"1_binaries\" WHERE name = 'export' AND app_id = " + str(
            app_id) + " AND member_id = " + str(member_id)
        result = self.submit_query(request, dbHost, dbName, login, password)
        return result[0][0]

    def getImportAppData(self, dbHost, dbName, login, password, member_id):
        request = "SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND member_id = " + str(member_id)
        result = self.submit_query(request, dbHost, dbName, login, password)
        return cursor.fetchall()[0][0]

    def getCountDBObjects(self, dbHost, dbName, login, password):
        tablesCount = {}
        tables = self.getEcosysTables(dbHost, dbName, login, password)
        for table in tables:
            tablesCount[table[2:]] = self.getCountTable(dbHost, dbName, login, password, table)
        return tablesCount

    def getTableColumnNames(self, dbHost, dbName, login, password, table):
        query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
                table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
        col = {}
        col = self.submit_query(query, dbHost, dbName, login, password)
        return col

    def getUserTableState(self, dbHost, dbName, login, password, userTable):
        request = "SELECT * FROM \"" + userTable + "\""
        res = self.submit_query(request, dbHost, dbName, login, password)
        col = self.getTableColumnNames(dbHost, dbName, login, password, userTable)
        table = {}
        for i in range(len(col)):
            table[col[i][0]] = res[0][i]
        return table

    def getUserTokenAmounts(self, dbHost, dbName, login, password):
        request = "select amount from \"1_keys\" ORDER BY amount"
        return self.submit_query(request, dbHost, dbName, login, password)

    def get_blockchain_hash(self, dbHost, dbName, login, password, maxBlockId):
        request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
            maxBlockId) + " ORDER BY id) AS t"
        return self.submit_query(request, dbHost, dbName, login, password)

    def get_system_parameter(self, dbHost, dbName, login, password, parameter):
        request = "select value from \"1_system_parameters\" WHERE name='" + parameter + "'"
        value = self.submit_query(request, dbHost, dbName, login, password)
        return value[0][0]

    def get_commission_wallet(self, dbHost, dbName, login, password, ecosId):
        request = "select value from \"1_system_parameters\" where name='commission_wallet'"
        wallets = self.submit_query(request, dbHost, dbName, login, password)
        wallet = json.loads(wallets[0][0])[0][1]
        return wallet

    def get_balance_from_db(self, dbHost, dbName, login, password, keyId):
        request = "select amount from \"1_keys\" WHERE id=" + keyId
        amount = self.submit_query(request, dbHost, dbName, login, password)
        balance = amount[0][0]
        return balance

    def get_balance_from_db_by_pub(self, dbHost, dbName, login, password, pub):
        connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
        cursor = connect.cursor()
        cursor.execute("select amount from \"1_keys\" WHERE pub='\\x" + pub + "'")
        amount = cursor.fetchall()
        return amount[0][0]

    def is_wallet_created(self, dbHost, dbName, login, password, pub):
        request = "select amount from \"1_keys\" WHERE id='" + pub + "'"
        wallet = self.submit_query(request, dbHost, dbName, login, password)
        if len(wallet) == 1 and wallet[0][0] == 1000000000000000000000:
            return True
        else:
            return False

    def get_block_gen_node(self, dbHost, dbName, login, password, block):
        request = "select node_position from \"block_chain\" WHERE id=" + block
        nodes = self.submit_query(request, dbHost, dbName, login, password)
        return nodes[0][0]

    def isCommissionInHistory(self, dbHost, dbName, login, password, idFrom, idTo, summ):
        request = "select * from \"1_history\" WHERE sender_id=" + idFrom + \
                       " AND recipient_id=" + str(idTo) + " AND amount=" + str(summ)
        rec = self.submit_query(request, dbHost, dbName, login, password)
        if len(rec) > 0:
            return True
        else:
            return False