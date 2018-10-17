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


#done
def get_ecosys_tables(url, token):
    tables = api.tables(url, token, 100)['list']
    list = []
    for table in tables:
        list.append(table['name'])
    return list

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

#done
def get_count_DB_objects(url, token):
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

#rollback2
def get_user_table_state(db, user_table):
    request = "SELECT * FROM \"" + user_table + "\""
    res = submit_query(request, db)
    col = get_table_column_names(db, user_table)
    table = {}
    for i in range(len(col)):
        table[col[i][0]] = res[0][i]
    return table

#done
def get_user_token_amounts(url, token):
    keys = api.list(url, token, 'keys')
    amounts = []
    for item in keys['list']:
        amounts.append(int(item['amount']))
    amounts.sort()
    return amounts

#block_chain
def get_blockchain_hash(db, max_block_id):
    request = "SELECT md5(array_agg(md5((t.id, t.hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
        max_block_id) + " ORDER BY id) AS t"
    return submit_query(request, db)


#cost
def get_balance_by_id(url, token, key_id, ecos=1):
    keys = api.list(url, token, 'keys')
    amounts = []
    for item in keys['list']:
        if item['id'] == str(key_id) and item['ecosystem'] == str(ecos):
            return item['amount']
    return None


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

#rollback2
def get_count_DB_objects_from_DB(dbHost, dbName, login, password):
	tablesCount = {}
	tables = get_ecosystem_tables_from_DB(dbHost, dbName, login, password)
	for table in tables:
		tablesCount[table[2:]] = get_count_table_from_DB(dbHost, dbName, login, password, table)
	return tablesCount

#rollback2
def get_ecosystem_tables_from_DB(dbHost, dbName, login, password):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'")
	tables = cursor.fetchall()
	list = []
	i = 0
	while i < len(tables):
		list.append(tables[i][0])
		i = i + 1
	return list

#rollback2
def get_count_table_from_DB(dbHost, dbName, login, password, table):
	connect = psycopg2.connect(host=dbHost, dbname=dbName, user=login, password=password)
	cursor = connect.cursor()
	cursor.execute("SELECT count(*) FROM \"" + table + "\"")
	return cursor.fetchall()[0][0]