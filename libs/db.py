import psycopg2
import json


from psycopg2.psycopg1 import cursor

from libs import api

#here
def submit_query(query, db):
    connect = psycopg2.connect(host=db["dbHost"], dbname=db["dbName"],
                               user=db["login"], password=db["pass"])
    cursor = connect.cursor()
    cursor.execute(query)
    return cursor.fetchall()    
    
#block_chain
def compare_node_positions(db, max_block_id, nodes):
    count_rec = nodes * 3 + nodes
    min_block = max_block_id - count_rec + 1
    request = "SELECT node_position, count(node_position) FROM block_chain WHERE id>" + str(
        min_block) + " AND id<" + str(max_block_id) + "GROUP BY node_position"
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

#limits
def is_count_tx_in_block(db, max_block_id, count_tx):
    min_block = max_block_id - 3
    request = "SELECT id, tx FROM block_chain WHERE id>" + str(min_block) + " AND id<" + str(max_block_id)
    tx = submit_query(request, db)
    i = 0
    while i < len(tx):
        if tx[i][1] > count_tx:
            print("Block " + str(tx[i][0]) + " contains " + \
                  str(tx[i][1]) + " transactions")
            return False
        i = i + 1
    return True

#api
#Returns list of all ecosystem tables
#can be changed to api.tables
def get_ecosys_tables1(db):
    request = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'"
    tables = submit_query(request, db)
    list = []
    i = 0
    while i < len(tables):
        list.append(tables[i][0])
        i = i + 1
    return list

def get_ecosys_tables(url, token):
    tables = api.tables(url, token, 100)['list']
    list = []
    for table in tables:
        list.append(table['name'])
    return list

#simvolio api rollback
#returns number of records in the table
#can be changed to api.table
def get_count_table(db, table):
    request = "SELECT count(*) FROM \"" + table + "\""
    return submit_query(request, db)

#protypo
#can be changed to actions.get_object_id
def get_founder_id(db):
    request = "SELECT value FROM \"1_parameters\" WHERE name = 'founder_account'"
    result = submit_query(request, db)
    return result[0][0]

#system_contracts
def get_export_app_data(db, app_id, member_id):
    request = "SELECT data as TEXT FROM \"1_binaries\" WHERE name = 'export' AND app_id = " + str(
        app_id) + " AND member_id = " + str(member_id)
    result = submit_query(request, db)
    return result[0][0]

#system_contracts
def get_import_app_data(db, member_id):
    request = "SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND member_id = " + str(member_id)
    result = submit_query(request, db)
    return result[0][0]

#block_chain compare_nodes
def get_count_DB_objects(db, url, token):
    tablesCount = {}
    tables = get_ecosys_tables(url, token)
    for table in tables:
        tablesCount[table[2:]] = get_count_table(db, table)
    return tablesCount

#TODO for Elena

#block_chain compare_nodes
def get_count_DB_objects(db, url, token):
    tables = {}
    list = api.tables(url, token)['list']
    for table in list:
        tables[table['name']] = table['count']
    return tables

#here
def get_table_column_names(db, table):
    query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
            table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
    col = {}
    col = submit_query(query, db)
    return col

#rollback1
def get_user_table_state(db, user_table):
    request = "SELECT * FROM \"" + user_table + "\""
    res = submit_query(request, db)
    col = get_table_column_names(db, user_table)
    table = {}
    for i in range(len(col)):
        table[col[i][0]] = res[0][i]
    return table

#block_chain
def get_user_token_amounts(db):
    request = "select amount from \"1_keys\" ORDER BY amount"
    return submit_query(request, db)

#block_chain
def get_blockchain_hash(db, max_block_id):
    request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
        max_block_id) + " ORDER BY id) AS t"
    return submit_query(request, db)

#limits
def get_system_parameter(db, parameter):
    request = "select value from \"1_system_parameters\" WHERE name='" + parameter + "'"
    value = submit_query(request, db)
    return value[0][0]

#cost
#can be changed to api.systemparams
def get_commission_wallet(db, ecosId):
    request = "select value from \"1_system_parameters\" where name='commission_wallet'"
    wallets = submit_query(request, db)
    wallet = json.loads(wallets[0][0])[0][1]
    return wallet

#cost
def get_balance_from_db(db, key_id):
    request = "select amount from \"1_keys\" WHERE id=" + key_id
    amount = submit_query(request, db)
    balance = amount[0][0]
    return balance

#cost
def get_balance_from_db_by_pub(db, pub):
    request = "select amount from \"1_keys\" WHERE pub='\\x" + pub + "'"
    amount = submit_query(request, db)
    return amount[0][0]

#API
def is_wallet_created(db, pub):
    request = "select amount from \"1_keys\" WHERE id='" + pub + "'"
    wallet = submit_query(request, db)
    if len(wallet) == 1 and wallet[0][0] == 1000000000000000000000:
        return True
    else:
        return False

#cost
def get_block_gen_node(db, block):
    request = "select node_position from \"block_chain\" WHERE id=" + str(block)
    nodes = submit_query(request, db)
    return nodes[0][0]

#contract_func
#may be it can be changed to db.table[count]
def get_max_id_from_table(db, table):
    request = "SELECT MAX(id) FROM \"" + table + "\""
    result = submit_query(request, db)
    return result[0][0]

#cost
def is_commission_in_history(db, id_from, id_to, summ):
    request = "select * from \"1_history\" WHERE sender_id=" + id_from + \
                   " AND recipient_id=" + str(id_to) + " AND amount=" + str(summ)
    rec = submit_query(request, db)
    if len(rec) > 0:
        return True
    else:
        return False

def is_commission_in_history_new(db_host, db_name, login, password, id_from, id_to, summ):
    connect = psycopg2.connect(host=db_host, dbname=db_name, user=login, password=password)
    cursor = connect.cursor()
    cursor.execute("select * from \"1_history\" WHERE sender_id=" + id_from +\
				 " AND recipient_id=" + str(id_to) + " AND amount=" + str(summ))
    rec = cursor.fetchall()
    if len(rec) > 0:
        return True
    else:
        return False