import unittest
import config
import os
import json

from libs.actions import Actions

class Rollback2(unittest.TestCase):
    
    def test_rollback1(self):
        self.conf = config.readMainConfig()
        host = self.conf["dbHost"]
        db = self.conf["dbName"]
        login = self.conf["login"]
        pas = self.conf["pass"]
        # Get from file all tables state
        dbInformation = Actions.getCountDBObjects(host, db, login, pas)
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
        dbUserTableInfo = Actions.getUserTableState(host, db, login, pas, tableName)
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
