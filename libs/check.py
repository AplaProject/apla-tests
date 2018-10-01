from libs import db, actions


def compare_nodes(config):
    nodes = len(config)
    amounts = []
    data = []
    max_block_id = []
    i = 0 
    while i < nodes:
        amounts.append(db.get_user_token_amounts(config[i]["db"]))
        data.append(actions.login(config[i]["url"], config[0]['private_key']))
        max_block_id.append(actions.get_max_block_id(config[i]["url"], data[i]["jwtToken"]))
        i += 1   

    max_block = max(max_block_id)
    hash = []
    i = 0 
    while i < nodes:
        hash.append(db.get_blockchain_hash(config[i]["db"], max_block))
        i += 1 
    node_position = db.compare_node_positions(config[0]["db"], max_block, nodes)
        
    main_dict = {"amounts": str(amounts[0]), "hash": str(hash[0]), "node_pos": "True"}
    dict = []
    i = 0 
    while i < nodes:
        dict.append({"amounts": str(amounts[i]),"hash": str(hash[i]),
                     "node_pos": str(node_position)})
        if main_dict != dict[i]:
            print ("Error in node " + str(i) + "dict Main is " + str(main_dict) +\
                   ", current is " + str(dict[i]))
            return False
        else:
            i += 1
    return True


def compare_db(config, url, token):
    nodes = len(config)
    dbInformation = []
    first_db = db.get_count_DB_objects(url, token)
    i = 1 
    while i < nodes:
        current_db = db.get_count_DB_objects(url, token)
        if current_db != first_db:
            print("Errorin db: Different info about " + str(current_db) +\
                  " != " + str(first_db) + " current node is " + str(i))
            return False
        i += 1
    return True