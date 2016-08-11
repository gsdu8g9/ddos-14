#!/usr/bin/python
from sklearn.externals import joblib
import pandas as pd
from pandas.io import sql
import psycopg2
import json

config = None


with open("config.json") as config_file:
    config = json.load(config_file)['database']


sql_query = "SELECT * FROM addresses ORDER BY time"

data = None


#connect to DB
with psycopg2.connect(host=config["host"], 
                      user=config["user"], 
                      password=config["password"], 
                      database=config["database"]) as conn:
    #fetch data
    data = sql.read_sql(sql_query, conn, index_col='id')

    data.time = data.time.map(lambda t: t.replace(microsecond=0))

    data_by_time = data.groupby(['time']).count()

    data['src'] = np.array(data.address.str.split('_').str.get(0))

    data_by_src = data.groupby(['time', 'src']).count()

    joblib.dump(data_by_time, "by_time.pkl")
    joblib.dump(data_by_src, "by_src.pkl")

    print("DONE")