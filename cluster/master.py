import json
from xmlrpc.server import SimpleXMLRPCServer
import logging
from multiprocessing import Process
import redis
import requests

WORKERS = {}
WORKER_ID = 0
JOB_ID = 0
global CONN

COUNTWORDS = "CountingWords"
WORDCOUNT = "WordCount"

def countingwords():
    pass


def submit_task(files, type):
    global JOB_ID
    global CONN

    filestr = files[1:-1]
    filestr = filestr.split(",")

    for file in filestr:
        task = {
            'JOBID': JOB_ID,
            'TypeTask': type,
            'fileurl': file
        }
        JOB_ID = JOB_ID + 1
        CONN.rpush('task:queue', json.dumps(task))

    if len(filestr) > 1:
        #Llamar a join
        pass

def submit_countingwords(files):
    submit_task(files, COUNTWORDS)


def submit_wordcount(files):
    submit_task(files, WORDCOUNT)


def add_worker():
    global WORKERS
    global WORKER_ID

    proc = Process(target=start_worker, args=(WORKER_ID,))
    proc.start()
    WORKERS[WORKER_ID] = proc

    WORKER_ID += 1

    return WORKER_ID


def delete_worker(id_worker):
    global WORKERS
    global WORKER_ID

    proc = WORKERS[id_worker]
    proc.kill()

    WORKER_ID -= 1


def list_workers():
    return str(WORKERS)


def start_worker():
    global CONN
    while True:
        task = CONN.blpop(['task:queue'], 0)
        task_json = json.loads(task[1])
        filestr = requests.get(task_json["fileurl"])
        type = task_json["TypeTask"]

        if type == WORDCOUNT:
            number = WordCount(filestr)
        elif type == COUNTWORDS:
            number = CountingWords(filestr)

        CONN.rpush(task_json["JOBID"], number)



def CountingWords(str):
    return len(str.split())

def WordCount(str):
    return 0


if __name__ == '__main__':
    CONN = redis.Redis()

    logging.basicConfig(level=logging.INFO)

    server = SimpleXMLRPCServer(('localhost', 9000))

    server.register_function(submit_countingwords, "submit_countingwords")
    server.register_function(submit_wordcount, "submit_wordcount")

    server.register_function(list_workers, "list_workers")
    server.register_function(add_worker, "add_worker")
    server.register_function(delete_worker, "delete_worker")

    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
