import psycopg2


# here
def submit_query(query, db):
    connect = psycopg2.connect(host=db['dbHost'], dbname=db['dbName'],
                               user=db['login'], password=db['pass'], port=db['port'])
    cursor = connect.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# block_chain
def compare_node_positions(db, max_block_id, nodes):
    count_rec = nodes * 3 + nodes # 12
    min_block = max_block_id - 10 + 1
    request = 'SELECT node_position, count(node_position) FROM block_chain WHERE id>' + str(
        min_block) + ' AND id<' + str(max_block_id) + 'GROUP BY node_position'
    positions = submit_query(request, db)
    countBlocks = round(count_rec / nodes / 10 * 7) 
    if len(positions) < nodes:
        print('One of nodes does not generate blocks' + str(positions))
        return False
    i = 0
    while i < len(positions):
        if positions[i][1] < countBlocks - 1:
            print('Node ' + str(i) + ' generated ' +
                  str(positions[i][1]) + ' blocks:' + str(positions))
            return False
        i = i + 1
    return True


# rollback2
def get_count_DB_objects_from_DB(db):
    tablesCount = {}
    tables = get_ecosystem_tables_from_DB(db)
    for table in tables:
        tablesCount[table[2:]] = get_count_table_from_DB(db, table)
    return tablesCount


# rollback2
def get_ecosystem_tables_from_DB(db):
    query = "select table_name from INFORMATION_SCHEMA.TABLES WHERE table_schema='public' AND table_name LIKE '1_%'"
    tables = submit_query(query, db)
    list = []
    i = 0
    while i < len(tables):
        list.append(tables[i][0])
        i = i + 1
    return list


# rollback2
def get_count_table_from_DB(db, table):
    query = "SELECT count(*) FROM \"" + table + "\""
    return submit_query(query, db)[0][0]


# here
def get_table_column_names(db, table):
    query = "SELECT pg_attribute.attname FROM pg_attribute, pg_class WHERE pg_class.relname='" + \
            table + "' AND pg_class.relfilenode=pg_attribute.attrelid AND pg_attribute.attnum>0"
    col = {}
    col = submit_query(query, db)
    return col


# rollback2
def get_user_table_state(db, user_table):
    request = "SELECT * FROM \"" + user_table + "\""
    res = submit_query(request, db)
    col = get_table_column_names(db, user_table)
    table = {}
    for i in range(len(col)):
        table[col[i][0]] = res[0][i]
    return table


# block_chain
def get_blockchain_hash(db, max_block_id):
    request = "SELECT md5(array_agg(md5((t.id, t.hash, t.rollbacks_hash, t.data, t.ecosystem_id, t.key_id, t.node_position, t.time, t.tx)::varchar))::varchar)  FROM (SELECT * FROM block_chain WHERE id <= " + str(
        max_block_id) + " ORDER BY id) AS t"
    return submit_query(request, db)


# block_chain
def get_table_hash(db, table):
    query = "select column_name from INFORMATION_SCHEMA.COLUMNS WHERE table_schema='public' AND table_name='" + table + "'"
    columns = submit_query(query, db)
    is_ecos_present = False
    s_col = ''
    for colum in columns:
        if str(colum[0]) == 'ecosystem':
            is_ecos_present = True
        s_col += 't.' + colum[0] + ', '
    if is_ecos_present:
        request = "SELECT md5(array_agg(md5((" + \
            s_col[:-2] + ")::varchar))::varchar)  FROM (SELECT * FROM \"" + \
            table + "\" ORDER BY id, ecosystem) AS t"
    else:
        request = "SELECT md5(array_agg(md5((" + \
            s_col[:-2] + \
            ")::varchar))::varchar)  FROM (SELECT * FROM \"" + \
            table + "\" ORDER BY id) AS t"
    return submit_query(request, db)[0][0]


# cost
def get_block_gen_node(db, block):
    request = "select node_position from \"block_chain\" WHERE id=" + \
        str(block)
    nodes = submit_query(request, db)
    return nodes[0][0]


# contract_func
def get_max_id_from_table(db, table):
    request = "SELECT MAX(id) FROM \"" + table + "\""
    result = submit_query(request, db)
    return result[0][0]


# system_contracts
def get_import_app_data(db, member_id):
    print('member_id', member_id)
    request = "SELECT value FROM \"1_buffer_data\" WHERE key = 'import' AND account = '" + \
        str(member_id) + "'"
    result = submit_query(request, db)
    return result[0][0]


# func for sorted DBFind test
def get_all_sorted_records_from_table(db, table):
    if table == 'keys' or table == 'members':
        request = 'SELECT id, ecosystem FROM "1_' + table + '" ORDER BY ecosystem, id LIMIT 250'
    else:
        request = 'SELECT id, name FROM "1_' + table + '" ORDER BY id LIMIT 250'
    result = submit_query(request, db)
    return result

def increase_blocks(db):
    request = 'UPDATE info_block SET block_id = block_id + 100'
    connect = psycopg2.connect(host=db['dbHost'], dbname=db['dbName'],
                               user=db['login'], password=db['pass'])
    cursor = connect.cursor()
    cursor.execute(request)
    connect.commit()
    
def change_hash_block_chain(db):
    request = "UPDATE block_chain SET rollbacks_hash = '0a0638f1411c71353f358fc4472f476ea10e8d8b6a3a17926489684c3aa08e72'"
    connect = psycopg2.connect(host=db['dbHost'], dbname=db['dbName'],
                               user=db['login'], password=db['pass'])
    cursor = connect.cursor()
    cursor.execute(request)
    connect.commit()
    
def change_hash_info_block(db):
    request = "UPDATE info_block SET rollbacks_hash = '0a0638f1411c71353f358fc4472f476ea10e8d8b6a3a17926489684c3aa08e72'"
    connect = psycopg2.connect(host=db['dbHost'], dbname=db['dbName'],
                               user=db['login'], password=db['pass'])
    cursor = connect.cursor()
    cursor.execute(request)
    connect.commit()
    
def change_content(db):
    request = "UPDATE \"1_greeting\" SET greeting='hacked' where id=1"
    connect = psycopg2.connect(host=db['dbHost'], dbname=db['dbName'],
                               user=db['login'], password=db['pass'])
    cursor = connect.cursor()
    cursor.execute(request)
    connect.commit()
    