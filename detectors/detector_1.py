#!/usr/bin/python
import sys, time, os
from multiprocessing import Process, Queue
from sklearn.externals import joblib
from sklearn.tree import DecisionTreeClassifier
from datetime import datetime
from storage import Storage
from sock import Sock

from config import config

sock = Sock({
    "port_in": config['detector_1']['port'],
    "port_out": config['detector_2']['port'],
    "ip_in": config['detector_1']['ip'],
    "ip_out": config['detector_1']['ip']
})


ATTACK_THRESHOLD = 2
attack_count = 0

model = None

# auto loading fresh model
def get_model():
    global model
    if not os.path.isfile(config['teacher']['lock_filename']):
        model = joblib.load("models_binary/all.pkl")
    return model


# listening socket
def process_socket(q):
    r = sock.socket_r()
    while True:
        pkg = sock.get_package(r)
        q.put(pkg)


# make predict by data
def process_data(q):
    s = sock.socket_s()
    global attack_count
    
    storage = Storage(config["database"])
    cur = storage.conn.cursor()

    while True:
        pkg = q.get()
        data = [int(x) for x in pkg.split(",")]
        pred = get_model().predict([data[1:]])
        
        print pkg, pred
        print "attacks in row", attack_count

        if pred[0] != 'BENIGN':
            attack_count += 1
            if attack_count > ATTACK_THRESHOLD:
                print "send", str(data[0])
                s.send(str(data[0]))
        else:
            # save to DB "table_all"
            # uniquePairsCount, bytesCount, packetsCount
            cur.execute("INSERT INTO table_all (time, ucount, pcount, bcount, target) VALUES (%s, %s, %s, %s, %s)", 
                        [datetime.now(), data[1], data[3], data[2], "BENIGN"])
            
            storage.conn.commit()

            attack_count = 0

def main():
    q1 = Queue()
    try:
        p_socket = Process(target=process_socket, args=(q1,))
        p_data = Process(target=process_data, args=(q1,))

        p_data.start()
        p_socket.start()

        while True:
            time.sleep(3600)

    except KeyboardInterrupt:
        print ("Caught KeyboardInterrupt, terminating workers")
        p_socket.terminate()
        p_data.terminate()
        storage.close()


if __name__ == "__main__":
    main()

