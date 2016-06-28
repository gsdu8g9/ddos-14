#!/usr/bin/python

import socket, sys, os, struct, time, signal, ConfigParser, json
from Queue import Empty
from multiprocessing import Process, Queue, Pipe

import json

config = None

with open("config.json") as config_file:
    config = json.load(config_file)['attack_service']


def send_udp_message(body):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(body, (config["IP"], config["PORT"]))


def send_attack_list(d):
    send_udp_message('atk:'+json.dumps(d))


def send_start(d):
    send_udp_message ('atk:'+json.dumps(d))


def send_end(d):
    send_udp_message ('atk_end:'+json.dumps(d))


def start_attack(id, command):
    os.system("ansible hunters -b -i ./hosts_for_attack"+str(id)+" -f 99 -a '"+command+"' > /dev/null")
    pass

def create_hosts_file(start, end, id):
    f = open('hosts_for_attack'+str(id), 'w')
    f.write('[hunters]' + '\n')
    for i in range (start,end+1):
        f.write(config[''] + str(i) + '\n')
    f.write('[hunters:vars]' + '\n')
    f.write('ansible_ssh_private_key_file=/home/ubuntu/cloud.key' + '\n')
    f.write('[ssh_connection]' + '\n')
    f.write('scp_if_ssh=True' + '\n')
    f.close()

def read_config(file_name):
    MIN_HUNTER_IP = config["MIN_HUNTER_IP"]
    MAX_HUNTER_IP = config["MAX_HUNTER_IP"]
    config = ConfigParser.ConfigParser()
    config.read(file_name)
    sections = config.sections()
    attacks = {}
    id = 0
    for section in sections:
        attacks[id] = {}
        attacks[id]['name'] = config.get (section, 'name')
        attacks[id]['command'] = config.get (section, 'command')
        attacks[id]['desc'] = config.get (section, 'desc')
        attacks[id]['start_time'] = config.getint (section, 'start_time')

        start_hunter_ip = MIN_HUNTER_IP
        end_hunter_ip = MAX_HUNTER_IP

        if config.has_option (section, 'start_hunter_ip'):
            start_hunter_ip = config.getint (section, 'start_hunter_ip')
        if config.has_option (section, 'end_hunter_ip'):
            end_hunter_ip = config.getint(section, 'end_hunter_ip')

        if (start_hunter_ip > MAX_HUNTER_IP) or (start_hunter_ip < MIN_HUNTER_IP):
            start_hunter_ip = MIN_HUNTER_IP
        if (end_hunter_ip > MAX_HUNTER_IP) or (end_hunter_ip < start_hunter_ip):
            end_hunter_ip = MAX_HUNTER_IP

        attacks[id]['start_hunter_ip'] = start_hunter_ip
        attacks[id]['end_hunter_ip'] = end_hunter_ip

        id += 1
    return attacks

def attack_process(id,data,q):
    create_hosts_file(data['start_hunter_ip'], data['end_hunter_ip'], id)
    time.sleep(data['start_time'])
    print('Start attack ' + str(id))
    q.put (('add_attack',{
                'id': id,
                'name': data['name'],
                'desc': data['desc']
        }))
    start_attack(id,data['command'])
    q.put (('del_attack',{'id': id}))
    print('End attack ' + str(id))


def init_attacks():
    print ('\033[92m'+'===================================================================================================='+'\033[0m')
    q1 = Queue()
    d = dict()
    attacks = read_config(sys.argv[1])
    process_list = {}
    for id, data in attacks.iteritems():
        process_list[id] = Process(target=attack_process, args=(id,data,q1))
        process_list[id].start()
    while True:
        alive = 0
        for id, p in process_list.iteritems():
            if p.is_alive():
                alive += 1
        if alive == 0:
            break
        try:
            type, data = q1.get_nowait()
        except Empty:
            time.sleep(0.001)
        else:
            if (type == 'add_attack'):
                d[data['id']] = {}
                d[data['id']]['name'] = data['name']
                d[data['id']]['desc'] = data['desc']
                send_start(d)
            if (type == 'del_attack'):
                send_end(d[data['id']])
                del d[data['id']]


def lock_file(fname):
    import fcntl
    _lock_file = open(fname, 'a+')
    try:
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return None
    return _lock_file


def check_dual_launch(file_name):
    lock = lock_file (file_name)
    if (lock == None):
        print ('Already running!')
        sys.exit(3)
    return lock


def main():
    lock = check_dual_launch('/tmp/s11_attacks')
    if (len(sys.argv)>=2):
        init_attacks()
        del lock
    else:
        print ('Enter config name')
        del lock
        sys.exit (2)


if __name__ == "__main__":
    main()

