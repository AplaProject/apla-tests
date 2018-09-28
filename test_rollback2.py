import unittest
import os
import json

from libs import db, tools

class Rollback2():
    
    def test_rollback2(self):
        self.unit = unittest.TestCase()
        self.conf = tools.read_config("main")
        print(self.conf)
        dbConf = self.conf["db"]
        lData = actions.login(self.conf[0]['url'], self.conf[0]['private_key'])
        token = lData["jwtToken"]
        # Get from file all tables state
        dbInformation = db.get_count_DB_objects(self.conf[0]['url'], token)
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'r') as dbF:
            data = dbF.read()
        dbJson = json.loads(data)
        # Check all tables
        for key in dbJson:
            db1 = dbInformation[key]
            db2 = dbJson[key]
            self.unit.assertEqual(db1, db2,"Different info about " + key)
        # Get from file user table name
        file = os.path.join(os.getcwd(), "userTableName.txt")
        with open(file, 'r') as f:
            tableName = f.read()
        # Get from file user table state
        dbUserTableInfo = db.get_user_table_state(dbConf, tableName)
        file = os.path.join(os.getcwd(), "dbUserTableState.json")
        with open(file, 'r') as dbUserFile:
            data = dbUserFile.read()
        dbUserJson = json.loads(data)
        # Check user table
        for key in dbUserJson:
            dbUser1 = dbUserTableInfo[key]
            dbUser2 = dbUserJson[key]
            self.unit.assertEqual(dbUser1, dbUser2, "Different info about in user table " + key)

