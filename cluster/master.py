from xmlrpc.server import SimpleXMLRPCServer
import logging
from multiprocessing import Process

WORKERS = {}
WORKER_ID = 0


def submit_countingwords(files):

    pass


def submit_wordcount(files):
    pass


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
    pass


if __name__ == '__main__':
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
