# ------------------------
# SISTEMAS DISTRIBUIDOS
# Gabriel Garcia, Ismael El-Fellah
# Fichero que expone la api MASTER con la que podra trabajar  el cliente y la logica de asignacion de tareas a workers
# -------------------------

import json
from xmlrpc.server import SimpleXMLRPCServer
import logging
from multiprocessing import Process
import redis
import requests

WORKERS = {}  # Tupla con ID de cada worker
WORKER_ID = 0
JOB_ID = 0
global CONN

COUNTWORDS = "CountingWords"
WORDCOUNT = "WordCount"
JOIN = "Join"
# -------------------------------------------------
# ------------ METODOS API MASTER -----------------
# -------------------------------------------------

# LLaman a submit task con el tipo de tasca correspondiente
def submit_countingwords(files):
    submit_task(files, COUNTWORDS)

def submit_wordcount(files):
    submit_task(files, WORDCOUNT)

# Crea un worker e inicia su subproceso correspondiente
def add_worker():
    global WORKERS
    global WORKER_ID

    # El proceso del worker ejecutara el metodo start_worker
    proc = Process(target=start_worker, args=(WORKER_ID,))
    proc.start()
    WORKERS[WORKER_ID] = proc

    WORKER_ID += 1

    return WORKER_ID

# Elimina un worker
def delete_worker(id_worker):
    global WORKERS
    global WORKER_ID

    proc = WORKERS[id_worker]
    proc.kill()  # Mata su proceso


# Devuelve lista con todos los workers creados
def list_workers():
    return str(WORKERS)


# -------------------------------------------------
# ------------ METODOS INTERNOS -------------------
# -------------------------------------------------

# Sube tasca a la cola de redis
def submit_task(files, type):
    global JOB_ID
    global CONN

    VECTOR_JOBID = {} # Vector para saber los identificadores de subprocesos pertenecientes a una misma invocacion
    filestr = files[1:-1]
    filestr = filestr.split(",")

    # Crea una task en la cola de redis por cada entrada de la invocacion
    i = 0
    for file in filestr:
        task = {
            'JOBID': JOB_ID,
            'TypeTask': type,
            'fileurl': file
        }
        VECTOR_JOBID[i] = JOB_ID    # Guardamos id por si es invocacion multiple
        JOB_ID = JOB_ID + 1
        i = i + 1;
        CONN.rpush('task:queue', json.dumps(task))

    # Si es una invocacion multiple
    if len(filestr) > 1:
        # Submit task de join
        task = {
            'JOBID': JOB_ID,
            'TypeTask': JOIN,
            'vector': VECTOR_JOBID
        }
        CONN.rpush('task:queue', json.dumps(task))

    pass

# Implementa la logica del tiempo de vida de cada proceso worker
def start_worker():
    global CONN
    # Solo acabara si se llama a delete worker
    while True:
        task = CONN.blpop(['task:queue'], 0)  # Coge una task de la cola de Redis
        task_json = json.loads(task[1])
        type = task_json["TypeTask"]  # Capturamos el tipo de tarea a ejecutar sobre el fichero

        # Llamada a las funciones
        if type == WORDCOUNT:
            filestr = requests.get(task_json["fileurl"])  # Captura contenido del fichero de la url (peticion request)
            number = WordCount(filestr)

        elif type == COUNTWORDS:
            filestr = requests.get(task_json["fileurl"])  # Captura contenido del fichero de la url (peticion request)
            number = CountingWords(filestr)

        # Si el proceso resulta encargado de joinear varias tareas de una invocacion multiple
        elif type == JOIN:
            vectorsubtasks = requests.get(task_json["vector"])  # Capturamos vector id subprocesos
            number = join_tasks(vectorsubtasks)

        # Pushea el resultado de cualquiera de las 3 posibles operaciones en la cola de redis con referencia al JOBID
        CONN.rpush(task_json["JOBID"], number)


# Cuenta numero de palabras del fichero capturadas en str(filestr)
def CountingWords(str):
    return len(str.split())


# Cuenta numero de cada palabra del fichero capturadas en str(filestr)
def WordCount(str):
    return 0

# Une tasks
def join_tasks(vectorsubtasks):
    pass

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
