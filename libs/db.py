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


def submit_query(query, db):
    connect = psycopg2.connect(host=db["dbHost"], dbname=db["dbName"],
                               user=db["login"], password=db["pass"])
    cursor = connect.cursor()
    cursor.execute(query)
    return cursor.fetchall()    
        
def compare_keys_cout(db):
    query = "SELECT key_id FROM block_chain Order by id DESC LIMIT 10"
    keys = submit_query(query, db)
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

def compare_node_positions(db, maxBlockId, nodes):
    count_rec = nodes * 3 + nodes
    minBlock = maxBlockId - count_rec + 1
    request = "SELECT node_position, count(node_position) FROM block_chain WHERE id>" + str(
        minBlock) + " AND id<" + str(maxBlockId) + "GROUP BY node_position"
    positions = submit_query(request, db)
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

def check_for_missing_node(db, minBlockId, maxBlockId):
    request = "SELECT node_position FROM block_chain WHERE id>=" + str(minBlockId) + " AND id<=" + str(maxBlockId)
    positions = submit_query(request, db)
    i = 0
    while i < len(positions):
        if positions[i][0] == 2:
            return False
        i = i + 1
    return True

def is_count_tx_in_block(db, maxBlockId, countTx):
    minBlock = maxBlockId - 3
    request = "SELECT id, tx FROM block_chain WHERE id>" + str(minBlock) + " AND id<" + str(maxBlockId)
    tx = submit_query(request, db)
    i = 0
    while i < len(tx):
        if tx[i][1] > countTx:
            print("Block " + str(tx[i][0]) + " contains " + \
                  str(tx[i][1]) + " transactions")
            return False
        i = i + 1
    return True
    
def get_count_records_block_chain(db):
    request = "SELECT count(*) FROM \"block_chain\""
    return submit_query(request, db)

def get_ten_items(db):
    request = "SELECT * FROM block_chain Order by id DESC LIMIT 10"
    return submit_query(request, db)

def get_ecosys_tables(db):
    request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'"
    tables = submit_query(request, db)
    list = []
    i = 0
    while i < len(tables):
        list.append(tables[i][0])
        i = i + 1
    return list

def get_ecosys_tables_by_id(db, ecosystemID):
    request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '" +\
        str(ecosystemID) + "_%'"
    tables = submit_query(request, db)
    list = []
    i = 0
    while i < len(tables):
        list.append(tables[i][0])
        i = i + 1
    return list

def get_count_table(db, table):
    request = "SELECT count(*) FROM \"" + table + "\""
    return submit_query(request, db)

def get_max_id_from_table(db, table):
    request = "SELECT MAX(id) FROM \"" + table + "\""
    result = submit_query(request, db)
    return result[0][0]

def execute_sql(db, query):
    return submit_query(query, db)

def get_object_id_by_name(db, table, name):
    request = "SELECT id FROM \"" + table + "\" WHERE name = '" + str(name) + "'"
    result = submit_query(request, db)
    return result[0][0]

def get_founder_id(db):
    request = "SELECT value FROM \"1_parameters\" WHERE name = 'founder_account'"
    result = submit_query(request, db)
    return result[0][0]

def get_system_parameter_value(db, name):
    request = "SELECT value FROM \"1_system_parameters\" WHERE name = '" + name + "'"
    result = submit_query(request, db)
    return result[0][0]

def get_export_app_data(db, app_id, member_id):
    request = "SELECT data as TEXT FROM \"1_binaries\" WHERE name = 'export' AND app_id = " + str(
        app_id) + " AND member_id = " + str(member_id)
    result = submit_query(request, db)
    return result[0][0]

def get_import_app_data(db, member_id):
    request = "SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND member_id = " + str(member_id)
    result = submit_query(request, db)
    return cursor.fetchall()[0][0]


def get_count_DB_objects(db):
    tablesCount = {}
    tables = get_ecosys_tables(db)
    for table in tables:
        tablesCount[table[2:]] = get_count_table(db, table)
    return tablesCount

def get_table_column_names(db, table):
    query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
            table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
    col = {}
    col = submit_query(query, db)
    return col

def get_user_table_state(db, userTable):
    request = "SELECT * FROM \"" + userTable + "\""
    res = submit_query(request, db)
    col = get_table_column_names(db, userTable)
    table = {}
    for i in range(len(col)):
        table[col[i][0]] = res[0][i]
    return table

def get_user_token_amounts(db):
    request = "select amount from \"1_keys\" ORDER BY amount"
    return submit_query(request, db)

def get_blockchain_hash(db, maxBlockId):
    request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
        maxBlockId) + " ORDER BY id) AS t"
    return submit_query(request, db)

def get_system_parameter(db, parameter):
    request = "select value from \"1_system_parameters\" WHERE name='" + parameter + "'"
    value = submit_query(request, db)
    return value[0][0]

def get_commission_wallet(db, ecosId):
    request = "select value from \"1_system_parameters\" where name='commission_wallet'"
    wallets = submit_query(request, db)
    wallet = json.loads(wallets[0][0])[0][1]
    return wallet

def get_balance_from_db(db, keyId):
    request = "select amount from \"1_keys\" WHERE id=" + keyId
    amount = submit_query(request, db)
    balance = amount[0][0]
    return balance

def get_balance_from_db_by_pub(db, pub):
    request = "select amount from \"1_keys\" WHERE pub='\\x" + pub + "'"
    amount = submit_query(request, db)
    return amount[0][0]

def is_wallet_created(db, pub):
    request = "select amount from \"1_keys\" WHERE id='" + pub + "'"
    wallet = submit_query(request, db)
    if len(wallet) == 1 and wallet[0][0] == 1000000000000000000000:
        return True
    else:
        return False

def get_block_gen_node(db, block):
    request = "select node_position from \"block_chain\" WHERE id=" + str(block)
    nodes = submit_query(request, db)
    return nodes[0][0]

def is_commission_in_history(db, idFrom, idTo, summ):
    request = "select * from \"1_history\" WHERE sender_id=" + idFrom + \
                   " AND recipient_id=" + str(idTo) + " AND amount=" + str(summ)
    rec = submit_query(request, db)
    if len(rec) > 0:
        return True
    else:
        return False