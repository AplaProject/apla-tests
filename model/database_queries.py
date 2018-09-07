
class DatabaseQueries(object):

    def __init__(self, _query=""):
        self._query = _query

    def __repr__(self):
        return self._query


    @classmethod
    def new_db_table(cls):
        return cls(_query='''
        [{"name":"MyName","type":"varchar",
        "index": "1",  "conditions":"true"},{"name":"Myb","type":"json",
        "index": "0",  "conditions":"true"}, {"name":"MyD","type":"datetime",
        "index": "0",  "conditions":"true"}, {"name":"MyM","type":"money",
        "index": "0",  "conditions":"true"},{"name":"MyT","type":"text",
        "index": "0",  "conditions":"true"},{"name":"MyDouble","type":"double",
        "index": "0",  "conditions":"true"},{"name":"MyC","type":"character",
        "index": "0",  "conditions":"true"}]
        ''')

    @classmethod
    def new_db_table_permissions(cls):
        return cls(_query='''
            {"insert": "false",
        "update" : "true","new_column": "true"}
            ''')

    @classmethod
    def new_db_table_2_column(cls, u_1, r_1, u_2, r_2):
        return cls(_query='''[
        {"name":"Text","type":"varchar", "index": "1",  "conditions": {"update": "true", "read": "true"}},
        {"name":"num","type":"varchar", "index": "0",  "conditions":{"update":"true", "read": "true"}}
        ]
        ''')

    @classmethod
    def new_db_table_updater_permissions(cls, r="true", i="true", u="true", new_column="true"):
        return cls(_query='{"read" : "'+r+'", "insert": "'+i+'", "update" : "'+u+'",  "new_column": "'+new_column+'"}')

    @classmethod
    def db_one_column(cls, name="MyName", type="varchar", index="1", conditions="true"):
        return cls(_query='[{"name": "'+name+'","type":"'+type+'", "index": "'+index+'", "conditions":"'+conditions+'"}]')

