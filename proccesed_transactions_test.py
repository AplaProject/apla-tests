import psycopg2
import config
import time

primaryCount = 0
a = 1
while a == 1:
    config.getDBConfig()
    connect = psycopg2.connect(host=config.config["dbHost"], dbname=config.config["dbName"], user=config.config["login"], password=config.config["pass"])
    cursor = connect.cursor()
    cursor.execute("SELECT count(*) FROM transactions_status where block_id>0 or error is not null")
    res = cursor.fetchall()
    currentCount = res[0][0]
    count = currentCount - primaryCount
    primaryCount = currentCount
    print(count)
    time.sleep(1)
