import unittest
import os
import json

from libs.actions import Actions
from libs.db import Db
from libs.tools import Tools

class Rollback2(unittest.TestCase):
    
    def test_rollback1(self):
        self.conf = Tools.read_config("nodes")
        db = self.conf["db"]
        # Get from file all tables state
<<<<<<< HEAD
        dbInformation = Db.get_count_DB_objects(host, db, login, pas)
=======
        dbInformation = Db.getCountDBObjects(db)
>>>>>>> 696a609e1b1d6a8b247a1ec6e4185df4f6321d8b
        file = os.path.join(os.getcwd(), "dbState.json")
        with open(file, 'r') as dbF:
            data = dbF.read()
        dbJson = json.loads(data)
        # Check all tables
        for key in dbJson:
            db1 = dbInformation[key]
            db2 = dbJson[key]
            self.assertEqual(db1, db2,"Different info about " + key)
        # Get from file user table name
        file = os.path.join(os.getcwd(), "userTableName.txt")
        with open(file, 'r') as f:
            tableName = f.read()
        # Get from file user table state
        dbUserTableInfo = Db.get_user_table_state(db, tableName)
        file = os.path.join(os.getcwd(), "dbUserTableState.json")
        with open(file, 'r') as dbUserFile:
            data = dbUserFile.read()
        dbUserJson = json.loads(data)
        # Check user table
        for key in dbUserJson:
            dbUser1 = dbUserTableInfo[key]
            dbUser2 = dbUserJson[key]
            self.assertEqual(dbUser1, dbUser2, "Different info about in user table " + key)

if __name__ == '__main__':
    unittest.main()
