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

if data is None:
    print("SOMETHING WRONG!!!")

else:
    #save addresses.pkl
    joblib.dump(data, "addresses.pkl")


    #close connection
    print("DONE")
