# ---------------------------------------------------------------------------------------------------------------------
# SISTEMAS DISTRIBUIDOS
# Gabriel Garcia, Ismael El-Fellah
# Fichero que expone la utilidad de invocar a las funciones de la api master a traves de los parametros:
#       --wcreate : crea worker
#       --wdelete <idworker> : elimina worker correspondiente a idworker
#       --wlist: lista workers
#       --runCW [paramsURL] : llama a counting words con los parametros indicados entre los corchetes
#       --runWC [paramsURL] : llama a word count con los parametros indicados entre los corchetes
#
# ---------------------------------------------------------------------------------------------------------------------
import xmlrpc.client
import click

global proxy

# Definicion parametros entrada y funcion cli() para gestionar las diferentes RPC sobre el master
@click.command()
@click.option('--wcreate', 'worker_create_flag', default=False, flag_value='wcreate', help='Create a worker')
@click.option('--wlist', 'worker_list_flag', default=False, flag_value='wlist', help='List all workers')
@click.option('--wdelete', default=-1, help='Delete a worker')
@click.option('--runcw', default="", help='Call CountingWords')
@click.option('--runwc', default="", help='Call WordCount')
def cli(worker_create_flag, worker_list_flag, wdelete, runcw, runwc):
    global proxy
    if worker_create_flag:
        print("Sucessfully createad worker with ID: " + str(proxy.add_worker()))
    if worker_list_flag:
        print(str(proxy.list_workers()))
    if wdelete != -1:
        proxy.delete_worker(wdelete)
    if runcw != "":
        print(proxy.submit_countingwords(runcw))
    if runwc != "":
        print(proxy.submit_wordcount(runwc))


# El main solo iniciara la conexion xmlrpc y llamara a la funcion que gestionara los parametros
if __name__ == '__main__':
    global proxy
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000', allow_none=True)
    cli()
