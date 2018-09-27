import string
import requests
import psycopg2
import json
import time

from collections import Counter
from genesis_blockchain_tools.crypto import sign
from genesis_blockchain_tools.crypto import get_public_key

from libs import db
from libs import actions


def compare_nodes(config):
    nodes = len(config)
    amounts = []
    data = []
    maxBlockId = []
    i = 0 
    while i < nodes:
        amounts.append(db.get_user_token_amounts(config[i]["db"]))
        data.append(actions.login(config[i]["url"], config[0]['private_key']))
        maxBlockId.append(actions.get_max_block_id(config[i]["url"], data[i]["jwtToken"]))
        i += 1   

    maxBlock = max(maxBlockId)
    hash = []
    i = 0 
    while i < nodes:
        hash.append(db.get_blockchain_hash(config[i]["db"], maxBlock))
        i += 1 
    node_position = db.compare_node_positions(config[0]["db"], maxBlock, nodes)
        
    mainDict = {"amounts": str(amounts[0]), "hash": str(hash[0]), "node_pos": "True"}
    dict = []
    i = 0 
    while i < nodes:
        dict.append({"amounts": str(amounts[i]),"hash": str(hash[i]),
                     "node_pos": str(node_position)})
        if mainDict != dict[i]:
            print ("Error in node " + str(i) + "dict Main is " + str(mainDict) +\
                   ", current is " + str(dict[i]))
            return False
        else:
            i += 1
    return True


def compare_db(config):
    nodes = len(config)
    dbInformation = []
    i = 0 
    while i < nodes:
        dbInformation.append(db.get_count_DB_objects(config[i]["db"]))
        dbInf = []
        for key in dbInformation[i]:
            dbInf.append(dbInformation[i][key])
        if(i > 0):
            if dbInf[i-1] != dbInf[i]:
                print("Errorin db: Different info about " + key)
                return False
        i += 1
    return True