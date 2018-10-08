from datetime import datetime
import time
import psycopg2


'''
Examles for start

python quickStarterMonitoring.py -dbHost=localhost -dbPort=5430 -dbName=genesis -dbUser=postgres -dbPassword=postgres -nodesCount=4 -timeout=5 -logAll=1

python quickStarterMonitoring.py -nodesCount=4
'''


def quick_starter_monitoring(request):

    db_params = {
        "dbHost": request.config.getoption('--dbHost'),
        'dbPort' : request.config.getoption('--dbPort'),
        'dbName' : request.config.getoption('--dbName'),
        'login' : request.config.getoption('--dbUser'),
        'password' : request.config.getoption('--dbPassword')
    }

    logAll = int(request.config.getoption('--logAll'))
    nodes_count = int(request.config.getoption('--nodesCount'))
    timeout = int(request.config.getoption('--timeout'))
    tables_list = []             # list of table names


    def get_count_db_objects(db_params):
        connect = psycopg2.connect(host=db_params['dbHost'],
                                   port=db_params['dbPort'],
                                   dbname=db_params['dbName'],
                                   user=db_params['login'],
                                   password=db_params['password'])

        global tables_list
        tables_list.clear()

        cursor = connect.cursor()
        result = {}

        cursor.execute("select count(*) from INFORMATION_SCHEMA.TABLES WHERE table_schema='public'")
        count_tables = cursor.fetchall()
        result["countTables"] = count_tables[0][0]
        tables_list.append('countTables')

        cursor.execute("SELECT count(*) FROM \"1_blocks\"")
        blocks = cursor.fetchall()
        result["blocks"] = blocks[0][0]
        tables_list.append('blocks')

        cursor.execute("SELECT count(*) FROM \"1_contracts\"")
        contracts = cursor.fetchall()
        result["contracts"] = contracts[0][0]
        tables_list.append('contracts')

        cursor.execute("SELECT count(*) FROM \"1_history\"")
        history = cursor.fetchall()
        result["history"] = history[0][0]
        tables_list.append('history')

        cursor.execute("SELECT count(*) FROM \"1_keys\"")
        keys = cursor.fetchall()
        result["keys"] = keys[0][0]
        tables_list.append('keys')

        cursor.execute("SELECT count(*) FROM \"1_languages\"")
        languages = cursor.fetchall()
        result["languages"] = languages[0][0]
        tables_list.append('languages')

        cursor.execute("SELECT count(*) FROM \"1_members\"")
        members = cursor.fetchall()
        result["members"] = members[0][0]
        tables_list.append('members')

        cursor.execute("SELECT count(*) FROM \"1_menu\"")
        menus = cursor.fetchall()
        result["menus"] = menus[0][0]
        tables_list.append('menus')

        cursor.execute("SELECT count(*) FROM \"1_notifications\"")
        notifications = cursor.fetchall()
        result["notifications"] = notifications[0][0]
        tables_list.append('notifications')

        cursor.execute("SELECT count(*) FROM \"1_pages\"")
        pages = cursor.fetchall()
        result["pages"] = pages[0][0]
        tables_list.append('pages')

        cursor.execute("SELECT count(*) FROM \"1_parameters\"")
        parameters = cursor.fetchall()
        result["parameters"] = parameters[0][0]
        tables_list.append('parameters')

        cursor.execute("SELECT count(*) FROM \"1_roles_assign\"")
        roles_assign = cursor.fetchall()
        result["roles_assign"] = roles_assign[0][0]
        tables_list.append('roles_assign')

        cursor.execute("SELECT count(*) FROM \"1_roles_list\"")
        roles_list = cursor.fetchall()
        result["roles_list"] = roles_list[0][0]
        tables_list.append('roles_list')

        cursor.execute("SELECT count(*) FROM \"1_sections\"")
        sections = cursor.fetchall()
        result["sections"] = sections[0][0]
        tables_list.append('sections')

        cursor.execute("SELECT count(*) FROM \"1_signatures\"")
        signatures = cursor.fetchall()
        result["signatures"] = signatures[0][0]
        tables_list.append('signatures')

        cursor.execute("SELECT count(*) FROM \"1_tables\"")
        tables = cursor.fetchall()
        result["tables"] = tables[0][0]
        tables_list.append('tables')

        cursor.execute("SELECT count(*) FROM \"block_chain\"")
        block_chain = cursor.fetchall()
        result["block_chain"] = block_chain[0][0]
        tables_list.append('block_chain')

        # confirmations - different from others

        cursor.execute("SELECT count(*) FROM \"info_block\"")
        info_block = cursor.fetchall()
        result["info_block"] = info_block[0][0]
        tables_list.append('info_block')

        cursor.execute("SELECT count(*) FROM \"install\"")
        install = cursor.fetchall()
        result["install"] = install[0][0]
        tables_list.append('install')

        cursor.execute("SELECT count(*) FROM \"log_transactions\"")
        log_transactions = cursor.fetchall()
        result["log_transactions"] = log_transactions[0][0]
        tables_list.append('log_transactions')

        cursor.execute("SELECT count(*) FROM \"migration_history\"")
        migration_history = cursor.fetchall()
        result["migration_history"] = migration_history[0][0]
        tables_list.append('migration_history')

        cursor.execute("SELECT count(*) FROM \"my_node_keys\"")
        my_node_keys = cursor.fetchall()
        result["my_node_keys"] = my_node_keys[0][0]
        tables_list.append('my_node_keys')

        # queue_blocks  - different from others
        # queue_tx - different from others

        cursor.execute("SELECT count(*) FROM \"rollback_tx\"")
        rollback_tx = cursor.fetchall()
        result["rollback_tx"] = rollback_tx[0][0]
        tables_list.append('rollback_tx')

        cursor.execute("SELECT count(*) FROM \"stop_daemons\"")
        stop_daemons = cursor.fetchall()
        result["stop_daemons"] = stop_daemons[0][0]
        tables_list.append('stop_daemons')

        cursor.execute("SELECT count(*) FROM \"system_contracts\"")
        system_contracts = cursor.fetchall()
        result["system_contracts"] = system_contracts[0][0]
        tables_list.append('system_contracts')

        cursor.execute("SELECT count(*) FROM \"system_parameters\"")
        system_parameters = cursor.fetchall()
        result["system_parameters"] = system_parameters[0][0]
        tables_list.append('system_parameters')

        cursor.execute("SELECT count(*) FROM \"system_states\"")
        system_states = cursor.fetchall()
        result["system_states"] = system_states[0][0]
        tables_list.append('system_states')

        cursor.execute("SELECT count(*) FROM \"system_tables\"")
        system_tables = cursor.fetchall()
        result["system_tables"] = system_tables[0][0]
        tables_list.append('system_tables')

        # transactions - different from others
        # transactions_status - different from others

        return result


    def get_all_db_responses(db_params):
        responses_array = []
        i = 0
        while i < nodes_count:
            dbname = ""
            dbname = "genesis" + str(i+1)
            db_params['dbName'] = dbname
            responses_array.append(get_count_db_objects(db_params))
            i = i + 1
        return responses_array


    def print_all_db_responses(responses):
        i = 0
        while i < nodes_count:
            print(responses[i])
            i = i + 1

    def verify_all_db_responses(responses):
        print("------------------------------------------------")
        print(str(datetime.now()) + "\n")
        res = responses
        i = 0
        while i < len(res)-1:
            j = i + 1
            while j < len(res):
                if res[i] != res[j]:
                    for index in range(len(tables_list)):
                        key = tables_list[index]

                        if (res[i][key] != res[j][key]) & (key == "block_chain"):
                            delta = abs(res[i][key] - res[j][key])
                            if delta>5:
                                print("ERROR: CountDBObjects: " + str(request.config.getoption('--dbName')) + str(i + 1) + " != " + str(request.config.getoption('--dbName')) + str(j + 1))
                                print(" Not Equals: " + str(tables_list[index]) + ": " + str(res[i][key]) + " != " + str(res[j][key]))
                            else:
                                if logAll == 1:
                                    if i != j:
                                        print("OK: " + str(request.config.getoption('--dbName')) + str(i + 1) + " = " + str(request.config.getoption('--dbName')) + str(j + 1))
                                        print(" " + str(tables_list[index]) + ": " + str(res[i][key]) + " != " + str(res[j][key]))

                        if (res[i][key] != res[j][key]) & (key != "block_chain"):
                            print("ERROR: CountDBObjects: " + str(request.config.getoption('--dbName')) + str(i + 1) + " != " + str(request.config.getoption('--dbName')) + str(j + 1))
                            print(" Not Equals: " + str(tables_list[index]) + ": " + str(res[i][key]) + " != " + str(res[j][key]))

                else:
                    if logAll == 1:
                        if i != j:
                            print("OK: " + str(request.config.getoption('--dbName')) + str(i + 1) + " = " + str(request.config.getoption('--dbName')) + str(j + 1))

                j = j + 1
            i = i + 1


    # Start script
    print("Start monitoring...")
    print("Nodes count = " + str(nodes_count))
    while True:
        res = get_all_db_responses(db_params)
        verify_all_db_responses(res)
        time.sleep(timeout)

