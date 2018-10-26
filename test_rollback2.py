import unittest
import os
import json

from libs import db, tools, actions

class TestRollback2():
    
    def test_rollback2(self):
        self.unit = unittest.TestCase()
        self.conf = tools.read_config("main")
        db_conf = self.conf["db"]
        # Get from file all tables state
        db_information = db.get_count_DB_objects_from_DB(db_conf)
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'r') as dbF:
            data = dbF.read()
        db_json = json.loads(data)
        # Check all tables
        for key in db_json:
            db1 = db_information[key]
            db2 = db_json[key]
            self.unit.assertEqual(int(db1), int(db2),"Different info about " + key)
        # Get from file user table name
        file = os.path.join(os.getcwd(), "userTableName.txt")
        with open(file, 'r') as f:
            tableName = f.read()
        # Get from file user table state
        db_user_table_info = db.get_user_table_state(db_conf, tableName)
        file = os.path.join(os.getcwd(), "dbUserTableState.json")
        with open(file, 'r') as dbUserFile:
            data = dbUserFile.read()
        db_user_json = json.loads(data)
        # Check user table
        for key in db_user_json:
            db_user1 = db_user_table_info[key]
            db_user2 = db_user_json[key]
            self.unit.assertEqual(db_user1, db_user2, "Different info about in user table " + key)
