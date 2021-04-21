# ---------------------------------------------------------------------------------------------------------------------
# SISTEMAS DISTRIBUIDOS
# Gabriel Garcia, Ismael El-Fellah
# Fichero que expone la api MASTER con la que podra trabajar  el cliente y la logica de asignacion de tareas a workers
# ---------------------------------------------------------------------------------------------------------------------
import ast
import json
from xmlrpc.server import SimpleXMLRPCServer
import logging
from multiprocessing import Process
import redis
import requests
from collections import Counter
import multiprocessing as mp
from mergedict import MergeDict
import secrets

mp.set_start_method('fork')

WORKERS = {}  # Tupla con ID de cada worker
WORKER_ID = 0
global CONN

COUNTWORDS = "CountingWords"
WORDCOUNT = "WordCount"
JOIN = "Join"


# -------------------------------------------------
# ------------ METODOS API MASTER -----------------
# -------------------------------------------------

# LLaman a submit task con el tipo de tasca correspondiente
def submit_countingwords(files):
    return submit_task(files, COUNTWORDS)


def submit_wordcount(files):
    return submit_task(files, WORDCOUNT)


# Crea un worker e inicia su subproceso correspondiente
def add_worker():
    global WORKERS
    global WORKER_ID

    # El proceso del worker ejecutara el metodo start_worker
    proc = Process(target=start_worker, args=(CONN,))
    proc.start()
    WORKERS[WORKER_ID] = proc

    WORKER_ID += 1

    return str(WORKER_ID)


# Elimina un worker
def delete_worker(id_worker):
    global WORKERS
    global WORKER_ID

    proc = WORKERS[id_worker]
    proc.kill()  # Mata su proceso
    WORKERS.pop(id_worker)


# Devuelve lista con todos los workers creados
def list_workers():
    return str(WORKERS)


# -------------------------------------------------
# ------------ METODOS INTERNOS -------------------
# -------------------------------------------------

# Sube tasca a la cola de redis
def submit_task(files, type):
    global CONN

    VECTOR_JOBID = {}  # Vector para saber los identificadores de subprocesos pertenecientes a una misma invocacion
    filestr = files[1:-1]
    filestr = filestr.split(",")

    # Crea una task en la cola de redis por cada entrada de la invocacion
    i = 0
    for file in filestr:
        job_id = secrets.token_urlsafe(8)
        task = {
            'JOBID': job_id,
            'TypeTask': type,
            'fileurl': file
        }
        VECTOR_JOBID[i] = job_id  # Guardamos id por si es invocacion multiple
        i = i + 1
        CONN.rpush('task:queue', json.dumps(task))

    # Si es una invocacion multiple
    if len(filestr) > 1:
        # Submit task de join
        job_id = secrets.token_urlsafe(8)
        task = {
            'JOBID': job_id,
            'TypeTask': JOIN,
            'Type': type,  # Type contendra el TypeTask de las tascas a hacer "join"
            'vector': VECTOR_JOBID
        }
        CONN.rpush('task:queue', json.dumps(task))

    # Esperara a que finalizen las tascas para retornar resultado al cliente
    resultat = CONN.blpop(job_id, 0)

    return "El resultado es:\n"+str(resultat[1])


# Implementa la logica del tiempo de vida de cada proceso worker
def start_worker(redis_conn):
    global CONN
    CONN = redis_conn
    # Solo acabara si se llama a delete worker
    while True:
        task = CONN.blpop(['task:queue'], 0)  # Coge una task de la cola de Redis
        task_json = json.loads(task[1])
        type = task_json["TypeTask"]  # Capturamos el tipo de tarea a ejecutar sobre el fichero

        # Llamada a las funciones
        if type == WORDCOUNT:
            filestr = requests.get(
                task_json["fileurl"]).content  # Captura contenido del fichero de la url (peticion request)
            number = WordCount(filestr)
            number = str(number).strip('[]')

        elif type == COUNTWORDS:
            filestr = requests.get(
                task_json["fileurl"]).content  # Captura contenido del fichero de la url (peticion request)
            number = CountingWords(filestr)

        # Si el proceso resulta encargado de joinear varias tareas de una invocacion multiple
        elif type == JOIN:
            # number = join_tasks(vectorsubtasks,type2)
            number = join_tasks(task_json)

        # Pushea el resultado de cualquiera de las 3 posibles operaciones en la cola de redis con referencia al JOBID
        CONN.rpush(task_json["JOBID"], number)


# Cuenta numero de palabras del fichero capturadas en str(filestr)
def CountingWords(str):
    a = len(str.split())
    return a


# Cuenta numero de cada palabra del fichero capturadas en str(filestr)
def WordCount(str):
    # Recorre el string y construye un diccionario con el numero de ocurrencias de cada palabra
    counts = dict()
    words = str.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts


# Une tasks
def join_tasks(task_json):
    nwords = 0
    vectorsubtasks = task_json["vector"]
    diccionario = {}
    type = task_json["Type"]
    # Si tenemos que joinear COUNTWORDS
    if type == COUNTWORDS:
        # Recorremos vectorsubtasks sumando el resultado de cada tasca de la cola de redis con indice JOBID
        for i in vectorsubtasks.values():
            # El redis retorna una tupla, donde la segunda posicion contiene el resultado de la tasca
            nwords += int(CONN.blpop(i, 0)[1])  # En caso de no finalizar se bloquea hasta que no llegue el resultado
        return nwords  # Pusheamos resultado final
    # Si es WORDCOUNT
    elif type == WORDCOUNT:
        for i in vectorsubtasks.values():
            # Counter() une sumando los diccionarios
            # El redis retorna una tupla, donde la segunda posicion contiene el resultado de la tasca en forma de string
            redistupla = CONN.blpop(i, 0)[1]
            # Con el ast.literal_eval convertimos el string de la 1a posicion de la tupla a diccionario para ir sumando
            diccionario = mergsum(ast.literal_eval(redistupla.decode('utf-8')), diccionario)
        return str(diccionario)

# Suma dos diccionarios
def mergsum(dictA, dictB):
    for key in dictB:
        if key in dictA:
            dictB[key] = dictB[key] + dictA[key]
        else:
            pass
    res = dictA | dictB
    return res

if __name__ == '__main__':
    CONN = redis.Redis()

    logging.basicConfig(level=logging.INFO)

    server = SimpleXMLRPCServer(('localhost', 9000), allow_none=True)

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
