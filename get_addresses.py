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



#connect to DB
conn = psycopg2.connect(host=config["host"], 
                        user=config["user"], 
                        password=config["password"], 
                        database=config["database"])




#fetch data
data = sql.read_sql(sql_query, conn, index_col='id')




#save addresses.pkl
joblib.dump(data, "addresses.pkl")




#close connection
print("DONE")
