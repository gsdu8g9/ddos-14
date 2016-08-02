from sklearn.tree import DecisionTreeClassifier, export_graphviz
from datetime import datetime, timedelta
from sklearn.externals import joblib
from tinterval import TimeInterval
from storage import Storage
from pandas.io import sql
import pandas as pd
import time
import os
import subprocess
import numpy as np

from config import config

lock_filename = config["teacher"]["lock_filename"]
last_time = None
storage = Storage(config['database'])
features = ['bcount', 'pcount', 'ucount']
THRESHOLD = 10

def teach():
    
    model_names = ['all', 's_d', 'd']
    global last_time
    
    # check .lock
    # mb change on while true... ?
    #if os.path.isfile(lock_filename):
    #        return
    while True:
        if not os.path.isfile(lock_filename):
            print "lock is disabled"
            break
        #print "lock is enabled"
        
    # doWork:
    # create lock
    with open(lock_filename, 'w') as lock:
        #for each model
        for model_name in model_names:
            print "prepare to teach:", model_name
            # prepare features names
            
            table_name = "table_" + model_name

            ### SAVE PARSED DATA IN ANOTHER TABLES
            #TODO: move in detector modules
            #load last data from RAW 
            #data = storage.select(t1=last_time)
            #print "len of data:", len(data)
            #df = storage.filter_data(data, nf_group_type=model_name)
            #print "len of dataframe:", len(df)
            #TODO: move in detector modules
            # save to DB
            #cur = storage.conn.cursor()
            #for index in xrange(len(df)):
            #    cur.execute("INSERT INTO " + table_name + " (time, ucount, pcount, bcount, target) VALUES (%s, %s, %s, %s, %s)", 
            #                (df.iloc[index].time, df.iloc[index].ucount, df.iloc[index].pcount, df.iloc[index].bcount, df.iloc[index].target))
            #storage.conn.commit()

            ### LOAD FULL PARSED DATA
            # load train_data
            cur = storage.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM table_" + model_name + " WHERE time >= %s", [datetime.fromtimestamp(last_time),])
            last_time_date_count = cur.fetchone()[0]
            print "len:", last_time_date_count
            cur.close()
            
            if last_time_date_count < THRESHOLD:
                continue
            
            train_data = sql.read_sql("SELECT * FROM " + table_name + " ORDER BY index", storage.conn, index_col='index')

            y = train_data.target
            X = train_data[features]
            
            print "len of train_data:", len(X)

            # train model
            # TODO: PARAMS SEARCH
            model = DecisionTreeClassifier(min_samples_split = 4, min_samples_leaf = 2, criterion='entropy', max_depth = 20)
            model.fit(X, y)

            # save model in file
            joblib.dump(model, model_name + ".pkl")
            visualize_tree(model, features, model_name)
            print "Finished for", model_name
    # remove lock
    os.remove(lock_filename)
    last_time = time.time()

def visualize_tree(clf, feature_names, model_name):
    
    fname = model_name + ".dot"
    with open(fname, 'w') as f:
        export_graphviz(clf, out_file=f, feature_names=feature_names)
    
    command = ["dot", "-Tpng", fname, "-o", model_name + ".png"]
    try:
        subprocess.check_call(command)
    except:
        exit("Could not run dot, ie graphviz, to produce visualization")

def main():
    
    print "started"
    if os.path.isfile(lock_filename):
        os.remove(lock_filename)

    action = TimeInterval(config['teacher']['interval'], teach)

    try:
        action.start()        

        while True:
            time.sleep(3600)

    except Exception as e:
        print e.message
        action.stop()
        storage.close()

    except KeyboardInterrupt:
        print ("Caught KeyboardInterrupt, terminating workers")
        action.stop()
        storage.close()
    
if __name__=="__main__":
    main()