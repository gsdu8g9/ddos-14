from sklearn.externals import joblib
from sqlalchemy import create_engine
from pandas.io import sql
import pandas as pd
import os

from storage import Storage

from config import config

config_db = config['database']

def load_training_data(s):
    d = joblib.load(s + ".dat")[['time', 'bcount', 'pcount', 'ucount', 'target']]
    return d

connection_string = 'postgresql://%s:%s@%s:%s/%s' % (config_db['user'], config_db['password'], config_db['host'], config_db['port'], config_db['database'])
engine = create_engine(connection_string)

print "CONNECTED"

data_all = load_training_data("100ALL")
data_all.to_sql('table_all', engine)
del data_all

print "table_all ADDED"

data_d = load_training_data("100D")
data_d.to_sql('table_d', engine)
del data_d

print "table_d ADDED"

data_s_d = load_training_data('100S_D')
data_s_d.to_sql('table_s_d', engine)
del data_s_d

print "table_s_d ADDED"